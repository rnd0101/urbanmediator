CREATE SEQUENCE locations_policy_table_id_seq;

CREATE TABLE locations_policy_table (
  id integer unique not null default nextval('locations_policy_table_id_seq'),
  location_id integer default NULL,
  user_id integer default NULL,
  role varchar(255) NOT NULL default '',
  adder_user_id integer default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);
