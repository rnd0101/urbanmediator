-- from mysql to postgresql
-- 1) auto_increment -> sequence (see below)
-- 2) int(11) -> integer
-- 3) double -> double precision
-- 4) datetime -> timestamp

BEGIN;

CREATE SEQUENCE datasources_id_seq;
CREATE SEQUENCE locations_id_seq;
CREATE SEQUENCE locations_datasources_id_seq;
CREATE SEQUENCE locations_users_tags_id_seq;
CREATE SEQUENCE notes_id_seq;
CREATE SEQUENCE project_users_id_seq;
CREATE SEQUENCE projects_points_id_seq;
CREATE SEQUENCE tag_namespaces_id_seq;
CREATE SEQUENCE tags_id_seq;
CREATE SEQUENCE users_id_seq;
CREATE SEQUENCE version_id_seq;
CREATE SEQUENCE user_profiles_id_seq;
CREATE SEQUENCE group_users_id_seq;
CREATE SEQUENCE groups_id_seq;
CREATE SEQUENCE triggers_id_seq;
CREATE SEQUENCE locations_policy_table_id_seq;
CREATE SEQUENCE location_profiles_id_seq;
CREATE SEQUENCE note_profiles_id_seq;
CREATE SEQUENCE profile_id_seq;

CREATE TABLE datasources (
  id integer unique not null default nextval('datasources_id_seq'),
  type varchar(30) default '',
  adapter varchar(128) default '',
  url varchar(255) NOT NULL default '',
  frequency integer default '86400',
  description text,
  private integer default '0',
  credentials varchar(255) NOT NULL default '',
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE locations (
  id integer unique not null default nextval('locations_id_seq'),
  lat double precision NOT NULL,
  lon double precision NOT NULL,
  title varchar(255) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  user_id integer NOT NULL,
  origin varchar(255) NOT NULL default '',
  ranking integer default '0',
  url varchar(255) NOT NULL default '',
  uuid varchar(2048) NOT NULL default '',
  begins timestamp default NULL,
  expires timestamp default NULL,
  ends timestamp default NULL,
  visible integer default '1',
  type varchar(30) default 'point',
  ord integer default '0',
  PRIMARY KEY  (id)
); 

CREATE TABLE locations_datasources (
  id integer unique not null default nextval('locations_datasources_id_seq'),
  datasource_id integer default NULL,
  location_id integer default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE locations_users_tags (
  id integer unique not null default nextval('locations_users_tags_id_seq'),
  location_id integer default NULL,
  user_id integer default NULL,
  tag_id integer default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE notes (
  id integer unique not null default nextval('notes_id_seq'),
  location_id integer default NULL,
  text text NOT NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  user_id integer NOT NULL,
  origin varchar(255) NOT NULL default '',
  ranking integer default '0',
  visible integer default '1',
  type varchar(30) default 'comment',
  ord integer default '0',
  PRIMARY KEY  (id)
);

CREATE TABLE project_users (
  id integer unique not null default nextval('project_users_id_seq'),
  project_id integer default NULL,
  user_id integer default NULL,
  role varchar(255) NOT NULL default '',
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE projects_points (
  id integer unique not null default nextval('projects_points_id_seq'),
  project_id integer default NULL,
  location_id integer default NULL,
  visible integer default '1',
  PRIMARY KEY  (id)
);

CREATE TABLE tag_namespaces (
  id varchar(64) NOT NULL default '',
  tag_system_id varchar(512) default NULL,
  PRIMARY KEY  (id)
);

CREATE TABLE tags (
  id integer unique not null default nextval('tags_id_seq'),
  tag varchar(255) default NULL,
  tag_namespace varchar(64) default NULL,
  PRIMARY KEY  (id)
);

CREATE TABLE users (
  id integer unique not null default nextval('users_id_seq'),
  username varchar(128) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  credentials VARCHAR(256) DEFAULT NULL,
  description VARCHAR (255),
  PRIMARY KEY  (id)
);

CREATE TABLE version (
  id integer unique not null default nextval('version_id_seq'),
  version varchar(100) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);


INSERT INTO tag_namespaces (id, tag_system_id) VALUES
    ('', 'http://icing.arki.uiah.fi/');
INSERT INTO tag_namespaces (id, tag_system_id) VALUES
    ('official', 'http://official.icing.arki.uiah.fi/');
INSERT INTO tag_namespaces (id, tag_system_id) VALUES
    ('status', 'http://issuereporter.icing.arki.uiah.fi');
INSERT INTO tag_namespaces (id, tag_system_id) VALUES
    ('special', 'http://special.icing.arki.uiah.fi/');

CREATE TABLE user_profiles (
  id integer unique not null default nextval('user_profiles_id_seq'),
  user_id INT,
  prop_key VARCHAR(128),  -- like "mail", "www", etc. - to be defined
  prop_type varchar(128) NOT NULL default 'text',
  prop_value TEXT,
  added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE group_users (
  id integer unique not null default nextval('group_users_id_seq'),
  group_id integer default NULL,
  user_id integer default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE groups (
  id integer unique not null default nextval('groups_id_seq'),
  groupname varchar(128) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

INSERT INTO groups (groupname) VALUES ('administrators');
INSERT INTO groups (groupname) VALUES ('users');
INSERT INTO groups (groupname) VALUES ('guests');

CREATE TABLE triggers (
  id integer unique not null default nextval('triggers_id_seq'),
  project_id integer default NULL,
  user_id integer default NULL,
  trigger_condition varchar(128) default '',  -- to be defined. 'addpoint', etc
  trigger_action text NOT NULL default '',
  adapter varchar(128) default '',
  url varchar(255) NOT NULL default '',
  frequency integer default '86400',
  description text,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  ord integer default '0',
  PRIMARY KEY (id)
);

CREATE TABLE locations_policy_table (
  id integer unique not null default nextval('locations_policy_table_id_seq'),
  location_id integer default NULL,
  user_id integer default NULL,
  role varchar(255) NOT NULL default '',
  adder_user_id integer default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE location_profiles (
    id integer unique not null default nextval('location_profiles_id_seq'),
    location_id integer,
    prop_key VARCHAR(128),  -- like "palette", "featured", etc. - to be defined
    prop_type varchar(128) NOT NULL default 'text',
    prop_value TEXT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE note_profiles (
    id integer unique not null default nextval('note_profiles_id_seq'),
    note_id integer,
    prop_key VARCHAR(128),
    prop_type varchar(128) NOT NULL default 'text',
    prop_value TEXT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE profile (
    id integer unique not null default nextval('profile_id_seq'),
    prop_key VARCHAR(128),
    prop_type VARCHAR(128) NOT NULL default 'text',
    prop_value TEXT,
    lang VARCHAR(10),
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);


INSERT INTO version (version) VALUES ('042-base');


CREATE FUNCTION CONCAT(varchar, varchar, varchar) RETURNS varchar
    AS 'select $1 || $2 || $3;'
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;

END;
