# Instance Tracking for Executable Models by Event Processing

Instance tracking allows distributed parties to monitor executable models, e.g., on AWS Step Functions. The client can operate in two ways. (1.) It observes AWS event logs and triggers smart contract function calls for events related to deploying models, starting instances, and reaching instance states. (2.) It observes the smart contract for events and appends an instance protocol stored in a database. The database allows for analysis of models, instances, and states with further dimensions according to the data model.

## Prototype

The prototype is implemented in Python 3.9, using the web3.py library for accessing blockchains. Additional node software running locally in a fully-validating configuration is required. The following Python 3 modules are required: Web3 requests base58 binascii hashlib.

Note: The prototype is only intended to demonstrate the feasibility of implementation.

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
