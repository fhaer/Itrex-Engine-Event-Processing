from .dwh import postgre_dwh

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

def load_events(m_events, i_events, s_events, t_events):
    
    if len(m_events) > 0 or len(i_events) > 0 or len(s_events) > 0 or len(t_events) > 0:

        connection = postgre_dwh.connect(SERVER, PORT, DATABASE, USER, K)
        
        for e in m_events:
            postgre_dwh.insert_model(connection, e[EVENT_MODEL_HASH], e[EVENT_METADATA])
            postgre_dwh.insert_event_type(connection, e[EVENT_TYPE], EVENT_MODEL_TYPE)
            postgre_dwh.insert_client(connection, e[EVENT_TRANSACTION_FROM], e[EVENT_CLIENT_ID])
            postgre_dwh.insert_contract(connection, e[EVENT_TRANSACTION_TO], e[EVENT_DEPLOYMENT_ADDRESS])
            postgre_dwh.insert_block(connection, e[EVENT_BLOCK_HASH], e[EVENT_BLOCK_NR], e[EVENT_BLOCK_TIMESTAMP])
            postgre_dwh.insert_transaction(connection, e[EVENT_TRANSACTION_HASH], e[EVENT_TRANSACTION_FROM], e[EVENT_TRANSACTION_TO], e[EVENT_BLOCK_HASH], e[EVENT_TRANSACTION_FEE_UNIT], e[EVENT_TRANSACTION_FEE], e[EVENT_TRANSACTION_UNIT_PRICE])
            postgre_dwh.insert_f_model(connection, e[EVENT_MODEL_HASH], e[EVENT_TRANSACTION_HASH], EVENT_MODEL_TYPE, e[EVENT_INDEX], e[EVENT_TIMESTAMP])
        for e in i_events:
            postgre_dwh.insert_instance(connection, e[EVENT_INSTANCE_HASH], e[EVENT_MODEL_HASH], e[EVENT_METADATA])
            postgre_dwh.insert_event_type(connection, e[EVENT_TYPE], EVENT_INSTANCE_TYPE)
            postgre_dwh.insert_client(connection, e[EVENT_TRANSACTION_FROM], e[EVENT_CLIENT_ID])
            postgre_dwh.insert_contract(connection, e[EVENT_TRANSACTION_TO], e[EVENT_DEPLOYMENT_ADDRESS])
            postgre_dwh.insert_block(connection, e[EVENT_BLOCK_HASH], e[EVENT_BLOCK_NR], e[EVENT_BLOCK_TIMESTAMP])
            postgre_dwh.insert_transaction(connection, e[EVENT_TRANSACTION_HASH], e[EVENT_TRANSACTION_FROM], e[EVENT_TRANSACTION_TO], e[EVENT_BLOCK_HASH], e[EVENT_TRANSACTION_FEE_UNIT], e[EVENT_TRANSACTION_FEE], e[EVENT_TRANSACTION_UNIT_PRICE])
            postgre_dwh.insert_f_instance(connection, e[EVENT_INSTANCE_HASH], e[EVENT_TRANSACTION_HASH], EVENT_INSTANCE_TYPE, e[EVENT_INDEX], e[EVENT_TIMESTAMP])
        for e in s_events:
            postgre_dwh.insert_state(connection, e[EVENT_STATE_HASH], e[EVENT_INSTANCE_HASH])
            postgre_dwh.insert_event_type(connection, e[EVENT_TYPE], EVENT_STATE_TYPE)
            postgre_dwh.insert_client(connection, e[EVENT_TRANSACTION_FROM], e[EVENT_CLIENT_ID])
            postgre_dwh.insert_contract(connection, e[EVENT_TRANSACTION_TO], e[EVENT_DEPLOYMENT_ADDRESS])
            postgre_dwh.insert_block(connection, e[EVENT_BLOCK_HASH], e[EVENT_BLOCK_NR], e[EVENT_BLOCK_TIMESTAMP])
            postgre_dwh.insert_transaction(connection, e[EVENT_TRANSACTION_HASH], e[EVENT_TRANSACTION_FROM], e[EVENT_TRANSACTION_TO], e[EVENT_BLOCK_HASH], e[EVENT_TRANSACTION_FEE_UNIT], e[EVENT_TRANSACTION_FEE], e[EVENT_TRANSACTION_UNIT_PRICE])
            postgre_dwh.insert_f_state(connection, e[EVENT_STATE_HASH], e[EVENT_TRANSACTION_HASH], EVENT_STATE_TYPE, e[EVENT_INDEX], e[EVENT_TIMESTAMP])

        postgre_dwh.commit_and_close(connection)
