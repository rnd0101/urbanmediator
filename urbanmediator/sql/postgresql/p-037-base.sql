CREATE SEQUENCE profile_id_seq;

CREATE TABLE profile (
    id integer unique not null default nextval('profile_id_seq'),
    prop_key VARCHAR(128),
    prop_type VARCHAR(128) NOT NULL default 'text',
    prop_value TEXT,
    lang VARCHAR(10),
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
