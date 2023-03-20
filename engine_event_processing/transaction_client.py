import sys
import json
import time
import os

from .transaction import node
from .transaction import data_coding
from .transaction import merkle_tree_hashing

DATA_DIR_MODELS = "data/models"
DATA_DIR_INSTANCES = "data/instances"
DATA_DIR_STATES = "data/states"

EVENT_MODEL = "model"
EVENT_MODEL_TYPE = 1
EVENT_MODEL_HASH = "modelHash"
EVENT_INSTANCE = "instance"
EVENT_INSTANCE_TYPE = 2
EVENT_INSTANCE_HASH = "instanceHash"
EVENT_STATE = "state"
EVENT_STATE_HASH = "stateHash"
EVENT_STATE_TYPE = 3
EVENT_TRANSITION = "transition"
EVENT_TRANSITION_TYPE = 4
EVENT_HASH = "hash"
EVENT_TYPE = "event"
EVENT_DATA = "data"
EVENT_CLIENT_ID = "clientId"
EVENT_METADATA = "metadata"
EVENT_ADDRESS = "address"
EVENT_DEPLOYMENT_ADDRESS = "deploymentAddress"

EVENT_TRANSACTION = "tx"
EVENT_TRANSACTION_FROM = "from"
EVENT_TRANSACTION_TO = "to"
EVENT_TRANSACTION_HASH = "transactionHash"
EVENT_TRANSACTION_FEE_UNIT = "transactionFeeUnit"
EVENT_TRANSACTION_FEE = "transactionFee"
EVENT_TRANSACTION_UNIT_PRICE = "transactionUnitPrice"

EVENT_BLOCK = "block"
EVENT_BLOCK_HASH = "blockHash"
EVENT_BLOCK_NR = "blockNumber"
EVENT_BLOCK_TIMESTAMP = "blockTimestamp"

EVENT_INDEX = "logIndex"
EVENT_TIMESTAMP = "timestamp"

def get_contract_address(node_web3):

    return node_web3.get_contract_address()

def connect_node(identity):
    
    node_web3 = node.Web3Node(identity)

    if not node_web3.w3.is_connected():
        print("web3 not connected, exiting")
        sys.exit()

    print("Client address:", identity.address)
    #print("Client private key:", data_coding.decode_binary_bytes32(identity.privatekey))
    print("Contract address:", get_contract_address(node_web3))

    return node_web3

def deploy_contract(node_web3):

    node_web3.deploy_contract()

def register_model(node_web3, identity, model_files):

    model_hash = merkle_tree_hashing.calculate_merkle_root(model_files)
    model_hash_bytes32 = data_coding.encode_binary_bytes32(model_hash)

    print("Register model ... \n")
    contract = node_web3.get_contract()

    transaction = node_web3.get_transaction()
    tx = contract.functions.registerModel(model_hash_bytes32, identity.address, model_hash_bytes32).buildTransaction(transaction)
    tx_hash = node_web3.send_transaction(tx)
    receipt = node_web3.w3.eth.waitForTransactionReceipt(tx_hash)

    # Optional event processing
    # https://web3py.readthedocs.io/en/v5/contracts.html?highlight=event#event-log-object
    #c = node_web3.get_contract()
    #c.events.myEvent().processReceipt(receipt)

def register_instance(node_web3, identity, model_files, instance_files):

    model_hash = merkle_tree_hashing.calculate_merkle_root(model_files)
    model_hash_bytes32 = data_coding.encode_binary_bytes32(model_hash)
    
    instance_hash = merkle_tree_hashing.calculate_merkle_root(instance_files)
    instance_hash_bytes32 = data_coding.encode_binary_bytes32(instance_hash)

    print("Register instance ... \n")
    contract = node_web3.get_contract()

    transaction = node_web3.get_transaction()
    tx = contract.functions.registerInstance(model_hash_bytes32, instance_hash, identity.address, instance_hash_bytes32).buildTransaction(transaction)
    tx_hash = node_web3.send_transaction(tx)
    receipt = node_web3.w3.eth.waitForTransactionReceipt(tx_hash)

def register_state(node_web3, identity, state_id, instance_files, state_file):

    instance_hash = merkle_tree_hashing.calculate_merkle_root(instance_files)
    instance_hash_bytes32 = data_coding.encode_binary_bytes32(instance_hash)

    state_files = [state_file]
    
    state_hash = merkle_tree_hashing.calculate_merkle_root(state_files)
    state_hash_bytes32 = data_coding.encode_binary_bytes32(state_hash)

    print("Register state ... \n")
    contract = node_web3.get_contract()

    transaction = node_web3.get_transaction()
    tx = contract.functions.registerState(instance_hash_bytes32, state_hash_bytes32).buildTransaction(transaction)
    tx_hash = node_web3.send_transaction(tx)
    receipt = node_web3.w3.eth.waitForTransactionReceipt(tx_hash)

def get_models(node_web3):

    models = {}

    contract = node_web3.get_contract()

    n = contract.caller.getNModels()

    for i in range(0, n):
        model_hash = contract.caller.models(i)
        model_desc = contract.caller.descriptor(model_hash)
        models[model_hash] = model_desc
        
    return models

def get_model_instance_state_files(node_web3, model_hash_bytes32):

    model_id = None
    model_file = None

    instance_ids = []
    instance_files = []

    state_files = []

    # search model with requested hash
    for path in os.listdir(DATA_DIR_MODELS):
        if os.path.isfile(os.path.join(DATA_DIR_MODELS, path)):
            file_hash = merkle_tree_hashing.calculate_merkle_root([path])
            file_hash_bytes32 = data_coding.encode_binary_bytes32(file_hash)
            if file_hash_bytes32 == model_hash_bytes32:
                model_file = path
                if model_file.endswith(".json"):
                    model_id = model_file[0:-5]

    # search instances
    for path in os.listdir(DATA_DIR_INSTANCES):
        if os.path.isfile(os.path.join(DATA_DIR_INSTANCES, path)):
            if path.startswith(model_id):
                instance_files.append(path)
                if path.endswith(".json"):
                    instance_ids.append(path[0:-5])

    # search states
    for path in os.listdir(DATA_DIR_STATES):
        if os.path.isfile(os.path.join(DATA_DIR_STATES, path)):
            for i_id in instance_ids:
                if path.startswith(i_id):
                    state_files.append(path)

    return (model_file, instance_files, state_files)

def is_model_registered(node_web3, model_files):

    model_hash = merkle_tree_hashing.calculate_merkle_root(model_files)
    model_hash_bytes32 = data_coding.encode_binary_bytes32(model_hash)

    contract = node_web3.get_contract()

    n = contract.caller.getNModels()

    for i in range(0, n):
        model_hash = contract.caller.models(i)
        if model_hash == model_hash_bytes32:
            return True
        
    return False

def is_instance_registered(node_web3, model_files, instance_files):

    model_hash = merkle_tree_hashing.calculate_merkle_root(model_files)
    model_hash_bytes32 = data_coding.encode_binary_bytes32(model_hash)

    instance_hash = merkle_tree_hashing.calculate_merkle_root(instance_files)
    instance_hash_bytes32 = data_coding.encode_binary_bytes32(instance_hash)

    contract = node_web3.get_contract()

    mh = contract.caller.instances(instance_hash_bytes32)
    if mh == model_hash_bytes32:
        return True
        
    return False

def is_state_registered(node_web3, instance_files, state_file):

    instance_hash = merkle_tree_hashing.calculate_merkle_root(instance_files)
    instance_hash_bytes32 = data_coding.encode_binary_bytes32(instance_hash)

    state_files = [state_file]
    
    state_hash = merkle_tree_hashing.calculate_merkle_root(state_files)
    state_hash_bytes32 = data_coding.encode_binary_bytes32(state_hash)

    contract = node_web3.get_contract()

    ih = contract.caller.states(state_hash_bytes32)
    if ih == instance_hash_bytes32:
        return True
        
    return False

def create_event_filters(node_web3, client_addr):

    # Create filters for events
    # https://web3py.readthedocs.io/en/v5/contracts.html?highlight=event#event-log-object

    reg_model_filter = node_web3.get_contract().events.RegisterModel.createFilter(
        fromBlock="0x0", argument_filters={} #, argument_filters={'from': client_addr}
        )
    reg_instance_filter = node_web3.get_contract().events.RegisterInstance.createFilter(
        fromBlock="0x0", argument_filters={} #, argument_filters={'from': client_addr}
        )
    reg_state_filter = node_web3.get_contract().events.RegisterState.createFilter(
        fromBlock="0x0", argument_filters={} #, argument_filters={'from': client_addr}
        )
    reg_transition_filter = node_web3.get_contract().events.RegisterTransition.createFilter(
        fromBlock="0x0", argument_filters={} #, argument_filters={'from': client_addr}
        )
    
    return (reg_model_filter, reg_instance_filter, reg_state_filter, reg_transition_filter)

def strip_0x(string):
    if string.startwith("0x"):
        return string[2:]
    return string

def get_events_from_filter(node_web3, ef, event_type, client_addr):

    events = []

    c_events = ef.get_new_entries()
    
    # https://web3py.readthedocs.io/en/v5/contracts.html?highlight=event#event-log-object
    for ce in c_events:
        
        print(ce)
        
        e = {}

        args = ce.get('args')
        
        from_addr = None
        to_addr = None
        value = None
        
        if not args is None:
            m_hash = args.get(EVENT_MODEL_HASH)
            i_hash = args.get(EVENT_INSTANCE_HASH)
            s_hash = args.get(EVENT_STATE_HASH)

            if m_hash:
                e[EVENT_MODEL_HASH] = strip_0x(data_coding.decode_binary_bytes32(m_hash))
            if i_hash:
                e[EVENT_INSTANCE_HASH] = strip_0x(data_coding.decode_binary_bytes32(i_hash))
            if s_hash:
                e[EVENT_STATE_HASH] = strip_0x(data_coding.decode_binary_bytes32(s_hash))

            e[EVENT_METADATA] = ce[EVENT_TYPE]

            e[EVENT_DEPLOYMENT_ADDRESS] = strip_0x(client_addr)
            e[EVENT_CLIENT_ID] = strip_0x(client_addr)

        blockHash = ce[EVENT_BLOCK_HASH].hex()
        
        block = node_web3.w3.get_block(blockHash)
        e[EVENT_BLOCK_HASH] = strip_0x(blockHash)
        e[EVENT_BLOCK_NR] = ce[EVENT_BLOCK_NR]
        e[EVENT_BLOCK_TIMESTAMP] = block["timestamp"]

        transactionHash = ce[EVENT_TRANSACTION_HASH].hex()
        transaction = node_web3.w3.get_transaction(transactionHash)
        e[EVENT_TRANSACTION_HASH] = strip_0x(transactionHash)
        e[EVENT_TRANSACTION_FROM] = strip_0x(transaction["from"])
        e[EVENT_TRANSACTION_TO] = strip_0x(transaction["to"])
        e[EVENT_TRANSACTION_FEE] = transaction["gas"]
        e[EVENT_TRANSACTION_FEE_UNIT] = "gas"
        if transaction["gasPrice"]:
            e[EVENT_TRANSACTION_UNIT_PRICE] = transaction["gasPrice"]
        else:
            e[EVENT_TRANSACTION_UNIT_PRICE] = 0

        e[EVENT_TYPE] = ce[EVENT_TYPE]
        e[EVENT_INDEX] = ce[EVENT_INDEX]
        e[EVENT_TIMESTAMP] = round(time.time())

        print(e)
        events.append(e)

    return events


def get_new_events(node_web3, m_filter, i_filter, s_filter, t_filter, client_addr):

    m_events = get_events_from_filter(node_web3, m_filter, EVENT_MODEL, client_addr)
    i_events = get_events_from_filter(node_web3, i_filter, EVENT_INSTANCE, client_addr)
    s_events = get_events_from_filter(node_web3, s_filter, EVENT_STATE, client_addr)
    t_events = get_events_from_filter(node_web3, t_filter, EVENT_TRANSITION, client_addr)

    return (m_events, i_events, s_events, t_events)
