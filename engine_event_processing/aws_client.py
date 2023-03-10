import sys
import json
import os.path

from .aws import step_functions

DATA_DIR_MODELS = "data/models"
DATA_DIR_INSTANCES = "data/instances"
DATA_DIR_STATES = "data/states"

def attach_listener(log_group, region):
    
    log_stream_prefix = "states/"
    time_since = "1m"

    step_functions.attach_to_cloud_watch(log_group, region, time_since)
    #attach_to_cloud_watch(log_group, region, time_since, log_stream_prefix=log_stream_prefix)

def get_models_states_instances(log_group, region, batch_n_minutes):
    
    log_stream_prefix = "states/"
    time_since = str(batch_n_minutes) + "m"

    (models, instances, state_events) = step_functions.get_cloud_watch_events(log_group, region, time_since)
    
    # TODO: filtering functionality, e.g. removal of matching states

    return (models, instances, state_events)

def get_instance_states(state_events):
    
    instance_state_events = {}
    
    for s_event in state_events:
        instance_id = s_event[step_functions.EVENT_INSTANCE_ID]

        if not instance_id in instance_state_events:
            instance_state_events[instance_id] = []
            
        instance_state_events[instance_id].append(s_event)
        
    return instance_state_events


def get_model_files(region, m_desc):

    id = m_desc[step_functions.EVENT_MODEL_ID]
    execution_arn = m_desc[step_functions.EVENT_EXECUTION_ARN]

    model_file = DATA_DIR_MODELS + "/" + id + ".json"

    if not os.path.exists(model_file):
        model = step_functions.load_model(execution_arn, region)
        f = open(model_file, "w")
        f.write(model)
        f.close()
        
    return [model_file]

def get_instance_files(region, i_desc):

    model_id = i_desc[step_functions.EVENT_MODEL_ID]
    instance_id = i_desc[step_functions.EVENT_INSTANCE_ID]
    execution_arn = i_desc[step_functions.EVENT_EXECUTION_ARN]

    instance_file = DATA_DIR_INSTANCES + "/" + model_id + "-" + instance_id + ".json"

    if not os.path.exists(instance_file):
        instance = step_functions.load_execution(execution_arn, region)
        f = open(instance_file, "w")
        f.write(instance)
        f.close()
    
    return [instance_file]

def get_state_files(instance_id, s_events):

    # construct observed traces and save states
    states = []
    trace = []

    for e in s_events:
        state = []

        for t_event in trace:
            state.append(t_event)    

        state.append(e)
        trace.append(e)

        states.append(state)

    # write states
    state_files = []

    for s in states:

        if len(s) > 0:
            state_id = s[-1][step_functions.EVENT_STATE_ID]
            instance_id = s[-1][step_functions.EVENT_INSTANCE_ID]
            model_id = s[-1][step_functions.EVENT_MODEL_ID]

            state_file = DATA_DIR_STATES + "/" + state_id + ".json"
            
            if not os.path.exists(state_file):
                f = open(state_file, "w")
                s_json = json.dumps(s)
                f.write(s_json)
                f.close()

            state_files.append(state_file)


    return state_files
