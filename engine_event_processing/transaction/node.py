import os
import subprocess
import sys
import binascii
import requests
import json
import time
from web3 import Web3

from . import contract

class Node:

	def __init__(self, working_dir):
		self.working_dir = working_dir

	def run_node(self):
		os.makedirs(self.working_dir, exist_ok=True)
		os.chdir(self.working_dir)

class Web3Node(Node):

	# Node Web Socket Connection
	#WEB3_ADDRESS = "ws://127.0.0.1:8546"
	WEB3_ADDRESS = "wss://sepolia.infura.io/ws/v3/74912c87bfa1416d83e7058653a83914"

	# Node HTTP Connection
	#WEB3_ADDRESS = "http://127.0.0.1:8545"
	#WEB3_ADDRESS = "https://mainnet.infura.io/v3/5cc53e4f3f614825be68d6aae4897cf4"

	def __init__(self, identity):
		self.account_address = Web3.to_checksum_address(identity.address)
		self.account_privatekey = identity.privatekey

		if self.WEB3_ADDRESS.startswith("ws"):
			provider = Web3.WebsocketProvider(self.WEB3_ADDRESS, websocket_timeout=60)
		else:
			provider = Web3.HTTPProvider(self.WEB3_ADDRESS)

		self.w3 = Web3(provider)

		# for proof-of-authority:
		#self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

		self.contract = None

	def get_contract(self):
		if self.contract is None:
			abi_file = os.path.dirname(__file__) + "/" + contract.ABI_FILE
			#print("Reading contract ABI from", abi_file)
			with open(abi_file) as f:
				abi = json.load(f)
				self.contract = self.w3.eth.contract(address=contract.ADDRESS, abi=abi)
		return self.contract
	
	def get_contract_address(self):
		return contract.ADDRESS

	def deploy_contract(self):
		import solcx
		solcx.install_solc()
		temp_file = solcx.compile_files(contract.SOL_FILE)
		abi = temp_file[contract.SOL_FILE + ":Itrex"]['abi']
		bytecode = temp_file[contract.SOL_FILE + ":Itrex"]['bin']
		Itrex = self.w3.eth.contract(abi=abi, bytecode=bytecode)
		construct_txn = Itrex.constructor().buildTransaction(
		{
			'from': self.account_address,
			'nonce': self.w3.eth.get_transaction_count(self.account_address),
		}
		)
		tx_create = self.w3.eth.account.sign_transaction(construct_txn, self.account_privatekey)
		tx_hash = self.w3.eth.send_raw_transaction(tx_create.rawTransaction)
		tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
		print(tx_receipt)


	def get_current_gas_price(self):
		gas_price_api = "https://www.etherchain.org/api/gasPriceOracle"
		r = requests.get(gas_price_api).json()
		gas_price = Web3.toWei(r['fastest'], 'gwei')

		if gas_price > 100000000000:
			print("Gas price exceeds 100 Gwei, abort")
			sys.exit()

		return gas_price

	def get_transaction(self):
		nonce = self.w3.eth.getTransactionCount(self.account_address)
		#block = self.w3.eth.getBlock("latest")

		gas_limit = 600000

		tx = {
				"from": self.account_address,
				"value": 0,
				'chainId': 1,
				'nonce': nonce,
				'gas': gas_limit,
		        'maxFeePerGas': 10000000,
		        'maxPriorityFeePerGas': 1000000,
				'chainId': 11155111
		}
		print("Transaction:", tx)

		return tx

	def send_transaction(self, tx):
		tx_hash = ""
		pk_b = self.account_privatekey
		signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=pk_b)
		tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
		time.sleep(0.5)
		return tx_hash
