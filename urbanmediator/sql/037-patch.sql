CREATE TABLE profile (
    id INT NOT NULL AUTO_INCREMENT,
    prop_key VARCHAR(128),
    prop_type VARCHAR(128) NOT NULL default 'text',
    prop_value TEXT,
    lang VARCHAR(10),
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

INSERT INTO version (version) VALUES ('037-patch');
