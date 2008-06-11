CREATE TABLE location_profiles (
    id INT NOT NULL AUTO_INCREMENT,
    location_id INT,
    prop_key VARCHAR(128),  -- like "palette", "featured", etc. - to be defined
    prop_type varchar(128) NOT NULL default 'text',
    prop_value TEXT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

INSERT INTO version (version) VALUES ('034-patch');
