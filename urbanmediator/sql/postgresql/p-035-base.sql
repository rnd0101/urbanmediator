CREATE SEQUENCE note_profiles_id_seq;

CREATE TABLE note_profiles (
    id integer unique not null default nextval('note_profiles_id_seq'),
    note_id integer,
    prop_key VARCHAR(128),
    prop_type varchar(128) NOT NULL default 'text',
    prop_value TEXT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
