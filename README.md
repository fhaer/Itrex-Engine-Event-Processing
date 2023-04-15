# Instance Tracking for Executable Models on Cloud Platforms and Blockchains

Instance tracking allows distributed parties to monitor executable models, e.g., on AWS Step Functions. The client application operates in two modes. (1) Execution control with model deployment and instantiation as well as triggering and tracking of AWS execution events for Step Function states and their smart contract registration. (2) Instance tracking and analysis allowing for publishing, listening, and subscribing to execution states at the client side as well as the server side instance protocol.

Note: The prototype is only intended to demonstrate the feasibility of implementation.

## Deployment Information

For testing purposes, the application has been deployed under the following addresses.

#### Client
- Account Address: 0xAcD398d9F25C40b1d292bfF2190A08D7D907c568
  - Transactions: https://sepolia.etherscan.io/address/0xAcD398d9F25C40b1d292bfF2190A08D7D907c568
- ENS Domain: [c-acd398d9f25c40b1d292bff2190a08d7d907c568.eth](https://app.ens.domains/name/c-acd398d9f25c40b1d292bff2190a08d7d907c568.eth/details)
- ENS URI Record: [https://c-acd398d9f25c40b1d292bff2190a08d7d907c568.host](https://c-acd398d9f25c40b1d292bff2190a08d7d907c568.host)
  - Certificate Fingerprint (SHA-256): 0x5350213c939a22175a665734f13eaf5bce4e42ecc26f2ac3d836450166558918
  - Certificate Fingerprint Signature (Ethereum ECDSA signature hash): 0x319a8127e02a87f9795b8d813220789b214181a7c4d40baa8bad2d80492e3b63340a407a10c39902a9ca86afcd16227922c5395fd549c43383b7a913db3881e91b (see https://etherscan.io/verifySig/16942)

#### Contract deployment on Ethereum Sepolia
- Account Address: 0x9817EECcf1F0Bd3d8685396551aD841A5837db5b
  - Transactions: https://sepolia.etherscan.io/address/0x9817EECcf1F0Bd3d8685396551aD841A5837db5b
- Account Address: 0x678Dc3b6316c031478a5F7Ad4D4E611CE1915262
  - Transactions: https://sepolia.etherscan.io/address/0x678Dc3b6316c031478a5F7Ad4D4E611CE1915262

## Prototype

The prototype is implemented in Python 3.9, using the web3.py library for accessing blockchains, with a smart contract in Solidity 0.8.18 for registering and distributing events, and database implementation for PostgreSQL 15 that stores instance states. Additional software, notably node software running locally in a fully-validating configuration, is required. 

Requirements: 
- Python 3.9 with modules web3 requests base58 psycopg2
- Ethereum node on the mainnet or the sepolia testnet with a web3 API
- PostgreSQL server 15
- AWS CLI
- [unbuffer](https://manpages.ubuntu.com/manpages/jammy/man1/unbuffer.1.html)

```
Usage: engine_event_processing.py <command>

Event processing for execution engines

Engine commands:
--aws-sf <log-group> <region> <min>  Process AWS Step Function events in <log-group> at AWS region <region> starting <min> minutes ago

Contract commands:
--contract <client-address>          Process smart contract events sent from <client-address> and load into database

Client account commands:
--create-account <client-id>         Create new Ethereum account linked to a user-specific <client-id>

```

Note: The prototype is only intended to demonstrate the feasibility of implementation.
