CREATE SEQUENCE location_profiles_id_seq;

CREATE TABLE location_profiles (
    id integer unique not null default nextval('location_profiles_id_seq'),
    location_id integer,
    prop_key VARCHAR(128),  -- like "palette", "featured", etc. - to be defined
    prop_type varchar(128) NOT NULL default 'text',
    prop_value TEXT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
