from web3 import Web3
import json

ADDRESS_STR = "0x678Dc3b6316c031478a5F7Ad4D4E611CE1915262"
ADDRESS = Web3.toChecksumAddress(ADDRESS_STR)

ABI_FILE = "contract.json"
SOL_FILE = "contract.sol"
