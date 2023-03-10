# Instance Tracking for Executable Models by Event Processing

Instance tracking allows distributed parties to monitor executable models, e.g., on AWS Step Functions. The client can operate in two ways. (1.) It observes AWS event logs and triggers smart contract function calls for events related to deploying models, starting instances, and reaching instance states. (2.) It observes the smart contract for events and appends an instance protocol stored in a database. The database allows for analysis of models, instances, and states with further dimensions according to the data model.
