import subprocess
import json
import re
import os
import sys
import io
import time
import psycopg2


def connect(server, port, database, user, password):
    
    print("Establishing database connection ...")

    conn = psycopg2.connect(
        host=server,
        port=port,
        database=database,
        user=user,
        password=password
        )

    return conn

def commit_and_close(connection):

    print("Commit and close...")
    connection.commit()
    connection.close()

def insert_model(connection, hash, metadata):
    c = connection.cursor()
    p = (hash, metadata)
    c.execute('INSERT INTO D_Model VALUES (%s, %s) ON CONFLICT DO NOTHING', p)

def insert_instance(connection, hash, hash_m, metadata):
    c = connection.cursor()
    p = (hash, hash_m, metadata)
    c.execute('INSERT INTO D_Instance VALUES (%s, %s, %s) ON CONFLICT DO NOTHING', p)

def insert_state(connection, hash, hash_i):
    c = connection.cursor()
    p = (hash, hash_i)
    c.execute('INSERT INTO D_State VALUES (%s, %s) ON CONFLICT DO NOTHING', p)

def insert_event_type(connection, event_type_name, event_type):
    c = connection.cursor()
    p = (event_type, event_type_name)
    c.execute('INSERT INTO D_Event_Type VALUES (%s, %s) ON CONFLICT DO NOTHING', p)

def insert_client(connection, client_address, client_id):
    c = connection.cursor()
    p = (client_address, client_id)
    c.execute('INSERT INTO D_Client VALUES (%s, %s) ON CONFLICT DO NOTHING', p)

def insert_contract(connection, ca_address, deployment_address):
    c = connection.cursor()
    p = (ca_address, deployment_address)
    c.execute('INSERT INTO D_Contract VALUES (%s, %s) ON CONFLICT DO NOTHING', p)

def insert_block(connection, block_hash, block_nr, block_timestamp):
    c = connection.cursor()
    p = (block_hash, block_nr, block_timestamp)
    c.execute('INSERT INTO D_Block VALUES (%s, %s, %s) ON CONFLICT DO NOTHING', p)

def insert_transaction(connection, hash, t_from, t_to, block_hash, fee_unit, fee, unit_price):
    c = connection.cursor()
    p = (hash, t_from, t_to, block_hash, fee_unit, fee, unit_price)
    c.execute('INSERT INTO D_Transaction VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING', p)

def insert_f_model(connection, hash, tx_hash, e_type, e_index, e_ts):
    c = connection.cursor()
    p = (hash, tx_hash, e_type, e_index, e_ts)
    c.execute('INSERT INTO F_Model VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING', p)

def insert_f_instance(connection, hash, tx_hash, e_type, e_index, e_ts):
    c = connection.cursor()
    p = (hash, tx_hash, e_type, e_index, e_ts)
    c.execute('INSERT INTO F_Instance VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING', p)

def insert_f_state(connection, hash, tx_hash, e_type, e_index, e_ts):
    c = connection.cursor()
    p = (hash, tx_hash, e_type, e_index, e_ts)
    c.execute('INSERT INTO F_State VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING', p)

def insert_f_transition(connection, hash_pre, hash_post, tx_hash, e_type, e_index, e_ts):
    c = connection.cursor()
    p = (hash_pre, hash_post, tx_hash, e_type, e_index, e_ts)
    c.execute('INSERT INTO F_Transition VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING', p)

