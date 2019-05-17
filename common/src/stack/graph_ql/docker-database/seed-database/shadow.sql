DROP TABLE IF EXISTS attributes;

CREATE TABLE attributes (
	id		INT AUTO_INCREMENT PRIMARY KEY,
	scope_map_id	INT NOT NULL,
	name		VARCHAR(128) NOT NULL,
	value		TEXT NOT NULL,
	INDEX (name),
	FOREIGN KEY (scope_map_id) REFERENCES cluster.scope_map(id) ON DELETE CASCADE
);
