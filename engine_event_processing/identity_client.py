from .identity import identity_client

KEYSTORE_DIR = "keystore"

def create_identity():
    web3c = identity_client.Web3Client(KEYSTORE_DIR)
    address_prvk = web3c.create_identity()
    return address_prvk

def initialize_identity():
    web3c = identity_client.Web3Client(KEYSTORE_DIR)
    if len(web3c.read_keystore()) < 1:
        web3c.create_identity()
    address_prvk = web3c.get_first_identity()
    return address_prvk

def get_identity():
    web3c = identity_client.Web3Client(KEYSTORE_DIR)
    address_prvk = web3c.get_first_identity()
    return address_prvk
