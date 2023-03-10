
SELECT *
FROM f_state f_s
	INNER JOIN d_state d_s on f_s.state_hash = d_s.state_hash 
	INNER JOIN d_instance d_i on d_s.instance_hash = d_i.instance_hash 
	INNER JOIN d_model d_m on d_i.model_hash = d_m.model_hash 
	INNER JOIN d_event_type d_e on f_s.event_type_id = d_e.event_type_id
	INNER JOIN d_transaction d_t on f_s.transaction_hash = d_t.transaction_hash 
	INNER JOIN d_block d_b on d_t.block_hash = d_b.block_hash 
	INNER JOIN d_client d_cl on d_t.client_address = d_cl.client_address 
	INNER JOIN d_contract d_co on d_t.ca_address = d_co.ca_address 
WHERE d_m.model_hash = 'c632cb64251cfdb18cb6dcab680b9fc82952aea783538ed246a4cb84f65b81e1';

SELECT event_type_name, f_s.state_hash, f_s.timestamp , d_b.block_nr, d_t.client_address, d_t.transaction_hash
FROM f_state f_s
	INNER JOIN d_state d_s on f_s.state_hash = d_s.state_hash 
	INNER JOIN d_instance d_i on d_s.instance_hash = d_i.instance_hash 
	INNER JOIN d_model d_m on d_i.model_hash = d_m.model_hash 
	INNER JOIN d_event_type d_e on f_s.event_type_id = d_e.event_type_id
	INNER JOIN d_transaction d_t on f_s.transaction_hash = d_t.transaction_hash 
	INNER JOIN d_block d_b on d_t.block_hash = d_b.block_hash 
WHERE 
	d_m.model_hash = 'c632cb64251cfdb18cb6dcab680b9fc82952aea783538ed246a4cb84f65b81e1' AND
	d_i.instance_hash = 'a681a01f3b9d2673b7fcf7f622274d55b4634ea313330c3705f631bee2ae779d';


SELECT d_m.model_hash, COUNT(f_s.state_hash) AS "n_states", 
	MIN(f_s.timestamp) AS "time_first_state", MAX(f_s.timestamp) AS "time_last_state"
FROM f_state f_s
	INNER JOIN d_state d_s on f_s.state_hash = d_s.state_hash 
	INNER JOIN d_instance d_i on d_s.instance_hash = d_i.instance_hash 
	INNER JOIN d_model d_m on d_i.model_hash = d_m.model_hash 
GROUP BY d_m.model_hash, d_i.instance_hash;
