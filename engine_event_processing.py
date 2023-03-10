import sys
import uuid
import getopt
import time

from engine_event_processing import aws_client
from engine_event_processing import transaction_client
from engine_event_processing import identity_client
from engine_event_processing import dwh_client

from time import perf_counter_ns

def print_usage():
    print("Usage: engine_event_processing.py <command>")
    print("")
    print("Event processing for execution engines")
    print("")
    print("Engine commands:")
    print("--aws-sf <log-group> <region> <min>  Process AWS Step Function events in <log-group> at AWS region <region> starting <min> minutes ago")
    print("")
    print("Contract commands:")
    print("--contract <client-address>          Process smart contract events sent from <client-address> and load into database")
    print("")
    print("Client account commands:")
    print("--create-account <client-id>         Create new Ethereum account linked to a user-specific <client-id>")
    print("")
    sys.exit()

def event_processing_aws_sp(args):

    log_group = ""
    region = ""
    batch_n_minutes = 5
    if len(args) > 1:
        log_group = args[0]
        region = args[1]
        batch_n_minutes = int(args[2])
    else:
        print_usage()

    client_acc = identity_client.get_identity()
    node = transaction_client.connect_node(client_acc)

    (models, instances, state_events) = aws_client.get_models_states_instances(log_group, region, batch_n_minutes)

    # instance runs
    for m_id in models.keys():
        m_desc = models[m_id]
        model_files = aws_client.get_model_files(region, m_desc)
        # if not registered: model deployment
        if not transaction_client.is_model_registered(node, model_files):
            transaction_client.register_model(node, client_acc, model_files)

    # instance runs
    for i_id in instances.keys():
        i_desc = instances[i_id]
        model_files = aws_client.get_model_files(region, i_desc)
        instance_files = aws_client.get_instance_files(region, i_desc)
        if not transaction_client.is_instance_registered(node, model_files, instance_files):
            transaction_client.register_instance(node, client_acc, model_files, instance_files)

    # state events
    instance_state_events = aws_client.get_instance_states(state_events)
    for instance_id in instance_state_events.keys():
        i_desc = instances[instance_id]
        instance_files = aws_client.get_instance_files(region, i_desc)
        
        events = instance_state_events[instance_id]
        states_by_file = aws_client.get_state_files(instance_id, events)

        for state_file in states_by_file:
            if not transaction_client.is_state_registered(node, instance_files, state_file):
                transaction_client.register_state(node, client_acc, model_files, instance_files, state_file)

    sys.exit(0)

    print("Time measurement start")
    t_start = perf_counter_ns()
    transaction_client.register_model(client_acc, ["data/m1"])
    t_stop = perf_counter_ns()
    print("Duration:\n", (t_stop-t_start))

def event_processing_contract_a2(args):

    region = ""
    contract_address = ""
    if len(args) > 1:
        region = args[0]
        contract_address = args[1]
    else:
        print_usage()

    if not contract_address:
        contract_address = transaction_client.get_contract_address(node)

    client_acc = identity_client.get_identity()
    node = transaction_client.connect_node(client_acc)
    
    batch_n_minutes = 60
    while True:

        models = transaction_client.get_models(node, model_files)

        for m_hash in models.keys():
            m_desc = models[m_hash]
            (m_file, i_files, s_files) = transaction_client.get_model_instance_state_files(node, m_hash)

            model_files = aws_client.get_model_files(region, m_hash)

        sys.exit(0)

def event_processing_contract(args):

    client_acc = identity_client.get_identity()
    node = transaction_client.connect_node(client_acc)
    
    client_addr = None
    if len(args) > 0:
        client_addr = args[0]
    else:
        client_addr = client_acc.address

    (m_filter, i_filter, s_filter, t_filter) = transaction_client.create_event_filters(node, client_addr)

    #prior_events = transaction_client.get_new_events(node, m_filter, i_filter, s_filter, t_filter)
    #print("Found", len(prior_events), "events before the most recent block")

    print("Listening for new events ...")
    while True:

        (m_events, i_events, s_events, t_events) = transaction_client.get_new_events(node, m_filter, i_filter, s_filter, t_filter, client_addr)
        dwh_client.load_events(m_events, i_events, s_events, t_events)
        time.sleep(10)


def create_account(args):

    print("Creating Ethereum account ...")
    client_acc = identity_client.create_identity()

    print("Registering account ...")
    client_id = args.get(0)
    if client_id is None:
        print("Client ID missing")
        sys.exit()

def process_cli():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ac", ["aws-sf", "contract", "create-account"])
    except getopt.GetoptError as err:
        print(err)
        print_usage()

    if len(opts) < 1:
        print_usage()

    for o, a in opts:
        if o in ("-a", "--aws-sf"):
            event_processing_aws_sp(args)
        elif o in ("-c", "--contract"):
            event_processing_contract(args)
        elif o == 'create-account':
            create_account(args)
        else:
            print_usage()

process_cli()
