import subprocess
import json
import re
import os
import sys
import io
import time

EVENT_ID = "id"
EVENT_MODEL_ID = "model_id"
EVENT_INSTANCE_ID = "instance_id"
EVENT_STATE_ID = "state_id"
EVENT_STATE_NAME = "state_name"
EVENT_TIMESTAMP = "timestamp"
EVENT_TIMESTAMP_START = "timestamp_start"
EVENT_TIMESTAMP_END = "timestamp_end"
EVENT_REGION = "region"
EVENT_CLIENT = "client"
EVENT_TYPE = "type"
EVENT_EXECUTION_ARN = "execution_arn"
EVENT_TASK_INPUT = "task_input"
EVENT_TASK_OUTPUT = "task_output"
EVENT_TASK_INPUT_DETAIL = "task_input_detail"
EVENT_TASK_OUTPUT_DETAIL = "task_output_detail"

def process_state_function_event(id, type, event_timestamp, execution_arn, task_details):
    state = task_details.get('name')
    task_input = task_details.get('input')
    task_output = task_details.get('output')
    task_input_detail = task_details.get('inputDetail')
    task_output_detail = task_details.get('outputDetail')
    
    if state:
        match = re.search(r'^arn:aws:states:(.+):(.+):execution:(.+):(.+)', execution_arn)
        if match:
            region = match.group(1)
            client = match.group(2)
            model_id = match.group(3)
            instance_id = match.group(4)

            state_id = model_id + "-" + instance_id + "-" + id

            s_event = { 
                EVENT_STATE_ID: state_id,
                EVENT_MODEL_ID: model_id,
                EVENT_INSTANCE_ID: instance_id,
                EVENT_STATE_NAME: state,
                EVENT_TIMESTAMP: event_timestamp,
                EVENT_REGION: region,
                EVENT_CLIENT: client,
                EVENT_TYPE: type,
                EVENT_ID: id
            }

            # event type examples:
            # TaskScheduled TaskStarted TaskStateEntered TaskStateExited TaskSucceeded
            # LambdaFunctionScheduled LambdaFunctionStarted LambdaFunctionSucceeded 
            # ChoiceStateEntered ChoiceStateExited
            # PassStateEntered PassStateExited 
            # SucceedStateEntered SucceedStateExited

            if type == "TaskStateEntered":
                s_event = { 
                    EVENT_STATE_ID: state_id,
                    EVENT_MODEL_ID: model_id,
                    EVENT_INSTANCE_ID: instance_id,
                    EVENT_STATE_NAME: state,
                    EVENT_TIMESTAMP: event_timestamp,
                    EVENT_REGION: region,
                    EVENT_CLIENT: client,
                    EVENT_TYPE: type,
                    EVENT_ID: id,
                    EVENT_TASK_INPUT: task_input,
                    EVENT_TASK_OUTPUT: task_output,
                    EVENT_TASK_INPUT_DETAIL: task_input_detail,
                    EVENT_TASK_OUTPUT_DETAIL: task_output_detail
                }

                state_events.append(s_event)

            #print(execution_arn, id, type, event_timestamp)


def process_model_and_instance(id, type, event_timestamp, execution_arn):
    model_id = None
    instance_id = None
    
    if type == "ExecutionStarted" or type == "ExecutionSucceeded":
        match = re.search(r'^arn:aws:states:(.+):(.+):execution:(.+):(.+)', execution_arn)
        if match:
            region = match.group(1)
            client = match.group(2)
            model_id = match.group(3)
            instance_id = match.group(4)

            if not model_id in models:
                model_desc = { 
                    EVENT_ID: id,
                    EVENT_MODEL_ID: model_id,
                    EVENT_REGION: region,
                    EVENT_CLIENT: client,
                    EVENT_TYPE: type,
                    EVENT_TIMESTAMP: event_timestamp,
                    EVENT_TIMESTAMP_START: event_timestamp,
                    EVENT_EXECUTION_ARN: execution_arn
                }
                models[model_id] = model_desc
            elif model_id in models and type == "ExecutionSucceeded":
                models[model_id][EVENT_TIMESTAMP_END] = event_timestamp

            if not instance_id in instances:
                instance_desc = { 
                    EVENT_ID: id,
                    EVENT_INSTANCE_ID: instance_id,
                    EVENT_MODEL_ID: model_id,
                    EVENT_REGION: region,
                    EVENT_CLIENT: client,
                    EVENT_TYPE: type,
                    EVENT_TIMESTAMP: event_timestamp,
                    EVENT_TIMESTAMP_START: event_timestamp,
                    EVENT_EXECUTION_ARN: execution_arn
                }
                instances[instance_id] = instance_desc
            elif instance_id in instances and type == "ExecutionSucceeded":
                instances[instance_id][EVENT_TIMESTAMP_END] = event_timestamp
            


def get_event_key(execution_arn, id):
    return execution_arn + "/" + id

def mark_event_processed(execution_arn, id):
    key = get_event_key(execution_arn, id)
    event_keys_processed.append(key)

def is_next_event(execution_arn, id, id_prev):
    key = get_event_key(execution_arn, id)
    key_prev_event = get_event_key(execution_arn, id_prev)
    if len(event_keys_processed) == 0:
        return True
    event_is_processed = (key in event_keys_processed)
    prev_event_is_processed = (key_prev_event in event_keys_processed)
    prev_event_is_undefined = (id_prev is None or id_prev == "0")
    return (not event_is_processed and (prev_event_is_processed or prev_event_is_undefined))

def buffer_event(timestamp, log_stream, event, execution_arn, id):
    key = get_event_key(execution_arn, id)
    if key not in event_keys_buffered:
        event_buffer.append([timestamp, log_stream, event])
        event_keys_buffered.append(key)

def remove_event_from_buffer(timestamp, log_stream, event, execution_arn, id):
    key = get_event_key(execution_arn, id)
    if key in event_keys_buffered:
        event_buffer.remove([timestamp, log_stream, event])
        event_keys_buffered.remove(key)

def process_log_events(timestamp, log_stream, event):
    # print(timestamp, (log_stream, event)
    # process event
    if all(key in event.keys() for key in ('id', 'type', 'details', 'event_timestamp', 'execution_arn')):
        # mandatory parameters
        event_id = event['id']
        event_type = event['type']
        event_details = event['details']
        event_timestamp = event['event_timestamp']
        event_execution_arn = event['execution_arn']
        # optional parameters
        event_id_prev = event.get('previous_event_id')

        # process buffered events first
        for event in event_buffer:
            process_log_events(event[0], event[1], event[2])
        if is_next_event(event_execution_arn, event_id, event_id_prev):
            process_model_and_instance(event_id, event_type, event_timestamp, event_execution_arn)
            process_state_function_event(event_id, event_type, event_timestamp, event_execution_arn, event_details)
            mark_event_processed(event_execution_arn, event_id)
            remove_event_from_buffer(timestamp, log_stream, event, event_execution_arn, event_id)
        else:
            buffer_event(timestamp, log_stream, event, event_execution_arn, event_id)
    else:
        print("--- Log message of unknown type ---")
        print(timestamp, log_stream, event)
        print("---")

def get_cloud_watch_cli(group, region, time_since, follow_stream, log_stream_prefix=None):
    
    log_format = "detailed" # json, detailed, short
    cli_read_timeout = "300" # 0 = no timeout
    cli_connect_timeout = "300" # 0 = no timeout

    # use aws logs tail with unbuffer to avoid buffered output to pipe
    # https://awscli.amazonaws.com/v2/documentation/api/latest/reference/logs/tail.html
    cli = ['unbuffer', 'aws', 'logs', 'tail', group, "--region", region, "--since", time_since, "--format", log_format, "--cli-read-timeout", cli_read_timeout, "--cli-connect-timeout", cli_connect_timeout, '--no-cli-pager', '--no-cli-auto-prompt', '--color', 'off']

    if follow_stream:
        cli.append('--follow')
    if log_stream_prefix:
        cli.extend(['--log-stream-name-prefix', log_stream_prefix])

    print(cli)
    return cli

def initialize():
    
    global event_keys_processed
    event_keys_processed = []

    global event_keys_buffered
    event_keys_buffered = []

    global event_buffer
    event_buffer = []

    global models
    models = {}

    global instances
    instances = {}

    global state_events
    state_events = []

def attach_to_cloud_watch(group, region, time_since, log_stream_prefix=None):

    initialize()

    # Read (1.) with buffered output (bufsize=1 for lines, >1 to set buffer size, =0 without buffer) and (2.) to a pipe where OS is buffering:
    # - when redirecting stdout to a pipe (stdout=subprocess.PIPE), the OS maintains a buffer and possibly output hangs before last buffer is filled
    # - solution 1: from Python 3.10 on, pipesize can be set, under linux, and stdout=subprocess.PIPE could be used with a small pipe size
    # - solution 2: under linux, "unbuffer <command>" can be used to unbuffer the pipe

    cli = get_cloud_watch_cli(group, region, time_since, True, log_stream_prefix=None)

    with subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True) as proc:

        while True:
            # blocking read of line
            line = proc.stdout.readline()
            #proc.stdout.seek(0, os.SEEK_END)
            #proc.stdout.flush()
            #sys.stdout.flush()
            #stdout, stderr = proc.communicate()
            #if line:
            #    print("x", line)
            #continue

            log_format = r'^(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d+\+\d\d:\d\d)\s(\S+)\s(.+)'
            match_line = re.search(log_format, line)
            if match_line:
                timestamp = match_line.group(1)
                log_stream = match_line.group(2)
                message = match_line.group(3)
                try:
                    json_message = json.loads(message)
                    process_log_events(timestamp, log_stream, json_message)
                except json.decoder.JSONDecodeError:
                    print("--- Log message without JSON content ---")
                    print(message)
                    print("---")
            else:
                print("--- Log message not machting format ---")
                print(line)
                print("---")

def attach_to_cloud_watch_async(group, region, time_since):

    initialize()

    from queue import Queue, Empty
    from threading import Thread
    
    ON_POSIX = 'posix' in sys.builtin_module_names

    cli = get_cloud_watch_cli(group, region, time_since, True, log_stream_prefix=None)

    def enqueue_output(out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    proc = subprocess.Popen(cli, stdout=subprocess.PIPE, bufsize=1, close_fds=ON_POSIX)
    q = Queue()
    t = Thread(target=enqueue_output, args=(proc.stdout, q))
    t.daemon = True # end thread with script
    t.start()
    time.sleep(1)
    # read line without blocking
    while True:
        try:
            line = q.get(timeout=.1)
        except Empty:
            continue
        else:
            print(line)

def get_cloud_watch_events(group, region, time_since):

    initialize()
    
    cli = get_cloud_watch_cli(group, region, time_since, False, log_stream_prefix=None)

    proc = subprocess.run(cli, stdout=subprocess.PIPE, bufsize=1, text=True)

    # blocking read of line
    for line in proc.stdout.splitlines():

        #print(line)

        log_format = r'^(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d+\+\d\d:\d\d)\s(\S+)\s(.+)'
        match_line = re.search(log_format, line)
        if match_line:
            timestamp = match_line.group(1)
            log_stream = match_line.group(2)
            message = match_line.group(3)
            try:
                json_message = json.loads(message)
                process_log_events(timestamp, log_stream, json_message)
            except json.decoder.JSONDecodeError:
                print("--- Log message without JSON content ---")
                print(message)
                print("---")
        else:
            print("--- Log message not machting format ---")
            print(line)
            print("---")

    return (models, instances, state_events)

def load_model(execution_arn, region):

    state_machine_arn = execution_arn
    m = re.search(r'^(.+):execution(:.+):(.+)$', execution_arn)
    if m:
        state_machine_arn = m.group(1) + ":stateMachine" + m.group(2)
    
    cli = ["aws", "stepfunctions", "describe-state-machine", "--state-machine-arn", state_machine_arn, "--region", region, "--output", "json"]
    
    proc = subprocess.run(cli, capture_output=True, text=True)

    model_str = proc.stdout
    model = json.loads(model_str)

    return model["definition"]

def load_execution(execution_arn, region):

    state_machine_arn = execution_arn
    m = re.search(r'^(.+):execution(:.+):(.+)$', execution_arn)
    if m:
        state_machine_arn = m.group(1) + ":stateMachine" + m.group(2)
    
    cli = ["aws", "stepfunctions", "list-executions", "--state-machine-arn", state_machine_arn, "--region", region, "--output", "json"]

    proc = subprocess.run(cli, capture_output=True, text=True)

    executions_str = proc.stdout
    executions = json.loads(executions_str)

    execution = {}

    if "executions" in executions:
        for e in executions["executions"]:
            if "executionArn" in e:
                if e["executionArn"] == execution_arn:
                    execution = e

    return json.dumps(execution)


# TODO: iterate state machines, set IAM role step-functions-role-1 to and enable logging in group step-functions/state-machines-group-1, https://docs.aws.amazon.com/step-functions/latest/dg/cw-logs.html

# TODO: iterate state machines, hash and emit deployment events for unknown machines; iterate executions, hash and emit instance events for unknown executions

