// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

/** 
 * @title Instance Tracking for Executable Models
 * @dev Implements an architecture for executable models and the tracking of their instances for decentralized applications.
 */
contract Itrex {

  // user account identifiers by address
  mapping(address => bytes32) public accounts;

  // models array
  bytes32[] public models;

  // model hash values by instance state hash value
  mapping(bytes32 => bytes32) public instances;

  // instance hash values by instance state hash value
  mapping(bytes32 => bytes32) public states;

  // instance hash values by transition hash value
  mapping(bytes32 => bytes32) public transitions;

  // descriptors for storing metadata by hash value 
  mapping(bytes32 => ModelInstanceDescriptor) public descriptors;

  // certificate fingerprints and signatures by client address
  mapping(address => bytes32) public certificateFingerprints;
  mapping(address => bytes16) public certificateSignaturesPrefix;
  mapping(address => bytes32) public certificateSignaturesA;
  mapping(address => bytes32) public certificateSignaturesB;

  // metadata for models and transitions
  struct ModelInstanceDescriptor {
      bytes32 metadata;
      address ownerAccount;
      uint blockTimestamp;
      bool isTerminated;
  }

  /** 
   * @dev notifies the client when models are registered
   */
  event RegisterModel(bytes32 indexed modelHash);
  
  /** 
   * @dev notifies the client when instances are registered for a model
   */
  event RegisterInstance(bytes32 indexed instanceHash, bytes32 modelHash);

  /** 
   * @dev notifies the client when states are registered for an instance
   */
  event RegisterState(bytes32 indexed stateHash, bytes32 instanceHash);

  /** 
   * @dev notifies the client when state transitions occur for an instance
   */
  event RegisterTransition(bytes32 indexed instance, bytes32 preState, bytes32 postState);

  /** 
   * @dev notifies the client when an instance is terminated
   */
  event TerminateInstance(bytes32 indexed instance);
  
  /** 
   * @dev notifies clients when a state was entered, where the state change was triggered by clientID
   */
  event ClientNotificationEvent(bytes32 indexed stateHash, address clientID);

  /** 
   * @dev registers an account with an ID chosen by the user
   */
  function registerAccount(bytes32 userID) public {
    accounts[msg.sender] = userID;
  }

  /** 
   * @dev registers a model with a 256 bit content-based model hash value
   */
  function registerModel(bytes32 modelHash, address ownerAccount, bytes32 metadata) public {
      models.push(modelHash);
      ModelInstanceDescriptor memory mid;
      mid.ownerAccount = ownerAccount;
      mid.metadata = metadata;
      mid.blockTimestamp = block.timestamp;
      descriptors[modelHash] = mid;

      emit RegisterModel(modelHash);
  }

  /** 
   * @dev registers for a given model an instance with a 256 bit content-based model hash value
   */
  function registerInstance(bytes32 modelHash, bytes32 instHash, address ownerAccount, bytes32 metadata) public {
      instances[instHash] = modelHash;
      ModelInstanceDescriptor memory mid;
      mid.ownerAccount = ownerAccount;
      mid.metadata = metadata;
      mid.blockTimestamp = block.timestamp;
      mid.isTerminated = false;
      descriptors[instHash] = mid;

      emit RegisterInstance(instHash, modelHash);
  }

  /** 
   * @dev registers for a given instance a state with a 256 bit content-based instance hash value
   */
  function registerState(bytes32 instHash, bytes32 stateHash) public {
      require(instances[instHash] > 0, "instance unknown");
      require(descriptors[instHash].ownerAccount == msg.sender, "state registration not permitted");
      require(descriptors[instHash].isTerminated == false, "instance is terminated");
      
      states[stateHash] = instHash;

      emit RegisterState(stateHash, instHash);
      emit ClientNotificationEvent(stateHash, msg.sender);
  }

  /** 
   * @dev registers a state, instance, and model using 256 bit content-based hash values
   */
  function registerState(bytes32 modelHash, bytes32 instHash, bytes32 stateHash) public {
      registerModel(modelHash, msg.sender, 0x0);
      registerInstance(modelHash, instHash, msg.sender, 0x0);

      require(instances[instHash] > 0, "instance unknown");
      require(descriptors[instHash].ownerAccount == msg.sender, "state registration not permitted");
      require(descriptors[instHash].isTerminated == false, "instance is terminated");
      
      states[stateHash] = instHash;

      emit RegisterState(stateHash, instHash);
      emit ClientNotificationEvent(stateHash, msg.sender);
  }

  /** 
   * @dev registers for a given instance a transition with two 256 bit content-based hash values of the corresponding pre- and post-states
   */
  function registerTransition(bytes32 instHash, bytes32 preStateHash, bytes32 postStateHash) public {
      require(instances[instHash] > 0, "instance unknown");
      require(descriptors[instHash].ownerAccount == msg.sender, "transition registration not permitted");
      require(descriptors[instHash].isTerminated == false, "instance is terminated");

      bytes32 transitionHash = getTransitionHash(preStateHash, postStateHash);
      transitions[instHash] = transitionHash;

      emitTransitionEvent(instHash, preStateHash, postStateHash);
      emit ClientNotificationEvent(postStateHash, msg.sender);
  }
  
  /** 
   * @dev registers certificates with fingerprint and signature with prefix, part A, and part B placed by clientAddress
   */
  function registerCertificate(address clientAddress, bytes32 fingerprint, bytes16 sigPrefix, bytes32 sigPartA, bytes32 sigPartB) public {
      require(clientAddress == msg.sender, "certificates can only be registered by the transaction sender");

      certificateFingerprints[clientAddress] = fingerprint;
      certificateSignaturesPrefix[clientAddress] = sigPrefix;
      certificateSignaturesA[clientAddress] = sigPartA;
      certificateSignaturesB[clientAddress] = sigPartB;
  }
  
  /** 
   * @dev terminates a running instance
   */
  function terminateInstance(bytes32 instHash) public {
      require(instances[instHash] > 0, "instance unknown");
      require(descriptors[instHash].ownerAccount == msg.sender, "termination of instance not permitted");
      
      descriptors[instHash].isTerminated = true;

      emit TerminateInstance(instHash);
  }

  /** 
   * @dev triggers a transition using a transition event as notification
   */
  function emitTransitionEvent(bytes32 instHash, bytes32 preStateHash, bytes32 postStateHash) public {
      require(instances[instHash] > 0, "instance unknown");
      require(states[preStateHash] > 0, "pre-state unknown");
      require(states[postStateHash] > 0, "post-state unknown");
      require(states[preStateHash] == states[postStateHash], "pre- and post-state are from different instances");
      require(descriptors[instHash].ownerAccount == msg.sender, "transition event not permitted");
      require(descriptors[instHash].isTerminated == false, "instance is terminated");

      emit RegisterTransition(instHash, preStateHash, postStateHash);
  }

  /** 
   * @dev retrieves a client by state hash
   */
  function getClient(bytes32 stateHash) public view returns (address) {
      bytes32 instanceId = states[stateHash];
      return descriptors[instanceId].ownerAccount;
  }

  /** 
   * @dev retrieves a certificate fingerprint and signature by client account address
   */
  function getCertificate(address client) public view returns (bytes32, bytes16, bytes32, bytes32) {
      return (certificateFingerprints[client], certificateSignaturesPrefix[client], certificateSignaturesA[client], certificateSignaturesB[client]);
  }

  /** 
   * @dev retrieves the instance of a state
   */
  function getInstance(bytes32 stateHash) public view returns (bytes32) {
      return states[stateHash];
  }

  /** 
   * @dev retrieves the model of an instance
   */
  function getModel(bytes32 instanceHash) public view returns (bytes32) {
      return instances[instanceHash];
  }

  /** 
   * @dev retrieves a transition by pre- and post-state
   */
  function getTransitionHash(bytes32 preStateHash, bytes32 postStateHash) private pure returns (bytes32) {
      bytes32 transitionHash = keccak256(abi.encodePacked(preStateHash, postStateHash));
      return transitionHash;
  }

  /** 
   * @dev retrieves an account with user ID by the hash value of a model or instance
   */
  function getAccount(bytes32 hash) public view returns (address account, bytes32 userID) {
      if (descriptors[hash].ownerAccount != address(0)) {
          address ownerAddress = descriptors[hash].ownerAccount;
          return (descriptors[hash].ownerAccount, accounts[ownerAddress]);
      }
  }

  /** 
   * @dev retrieves metadata of a model or instance by hash value
   */
  function getMetadata(bytes32 hash) public view returns (bytes32) {
      return descriptors[hash].metadata;
  }

  /** 
   * @dev changes the access permissions to an instance, identified by a hash value, to a given account
   */
  function delegate(bytes32 hash, address ownerAccount) public {
      require(descriptors[hash].ownerAccount == msg.sender, "delegate not permitted");

      descriptors[hash].ownerAccount = ownerAccount;
  }

  /**
   * returns the number of registered models
   */ 
  function getNModels() public view returns (uint) {
      return models.length;
  }

}
