CREATE TABLE note_profiles (
    id INT NOT NULL AUTO_INCREMENT,
    note_id INT,
    prop_key VARCHAR(128),
    prop_type varchar(128) NOT NULL default 'text',
    prop_value TEXT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

INSERT INTO version (version) VALUES ('035-patch');
