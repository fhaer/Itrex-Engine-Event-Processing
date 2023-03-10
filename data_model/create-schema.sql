drop table if exists F_Model, F_Instance, F_State, F_Transition;
drop table if exists D_State, D_Instance, D_Model;
drop table if exists D_Event_Type;
drop table if exists D_Transaction;
drop table if exists D_Block;
drop table if exists D_Contract;
drop table if exists D_Client;

create table D_Model (model_hash char(64) primary key, model_metadata text);
create table D_Instance (instance_hash char(64) primary key, model_hash char(64)references D_Model(model_hash), instance_metadata text);
create table D_State (state_hash char(64) primary key, instance_hash char(64) references D_Instance(instance_hash));

create table D_Client (client_address char(40) primary key, client_id text);
create table D_Contract (ca_address char(40) primary key, deployment_address char(40) references D_Client(client_address));
create table D_Block (block_hash char(64) primary key, block_nr int, block_timestamp text);

create table D_Transaction (
	transaction_hash char(64) primary key, 
	client_address char(40) references D_Client(client_address),
	ca_address char(40) references D_Contract(ca_address),
	block_hash char(64) references D_Block(block_hash),
	transaction_fee_unit varchar(4),
	transaction_fee decimal(16, 8),
	transaction_unit_price decimal(16, 8)
);

create table D_Event_Type (
	event_type_id int primary key,
	event_type_name text
);

create table F_Model (
	model_hash char(64),
	transaction_hash char(64),
	event_type_id int,
	event_index int,
	timestamp text,
	primary key (model_hash, transaction_hash, event_type_id),
	foreign key (model_hash) references D_Model(model_hash),
	foreign key (transaction_hash) references D_Transaction(transaction_hash),
	foreign key (event_type_id) references D_Event_Type(event_type_id)
);

create table F_Instance (
	instance_hash char(64),
	transaction_hash char(64),
	event_type_id int,
	event_index int,
	timestamp text,
	primary key (instance_hash, transaction_hash, event_type_id),
	foreign key (instance_hash) references D_Instance(instance_hash),
	foreign key (transaction_hash) references D_Transaction(transaction_hash),
	foreign key (event_type_id) references D_Event_Type(event_type_id)
);

create table F_State (
	state_hash char(64),
	transaction_hash char(64),
	event_type_id int,
	event_index int,
	timestamp text,
	primary key (state_hash, transaction_hash, event_type_id),
	foreign key (state_hash) references D_State(state_hash),
	foreign key (transaction_hash) references D_Transaction(transaction_hash),
	foreign key (event_type_id) references D_Event_Type(event_type_id)
);

create table F_Transition (
	pre_state_hash char(64),
	post_state_hash char(64),
	transaction_hash char(64),
	event_type_id int,
	event_index int,
	timestamp text,
	primary key (pre_state_hash, post_state_hash, transaction_hash, event_type_id),
	foreign key (pre_state_hash) references D_State(state_hash),
	foreign key (post_state_hash) references D_State(state_hash),
	foreign key (transaction_hash) references D_Transaction(transaction_hash),
	foreign key (event_type_id) references D_Event_Type(event_type_id)
);

