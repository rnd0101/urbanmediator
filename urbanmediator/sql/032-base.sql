CREATE TABLE datasources (
  id int(11) NOT NULL auto_increment,
  type varchar(30) default '',
  adapter varchar(128) default '',
  url varchar(255) NOT NULL default '',
  frequency int(11) default '86400',
  description text,
  private int(11) default '0',
  credentials varchar(255) NOT NULL default '',
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE locations (
  id int(11) NOT NULL auto_increment,
  lat double NOT NULL,
  lon double NOT NULL,
  title varchar(255) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  user_id int(11) NOT NULL,
  origin varchar(255) NOT NULL default '',
  ranking int(11) default '0',
  url varchar(255) NOT NULL default '',
  uuid varchar(2048) NOT NULL default '',
  begins datetime default NULL,
  expires datetime default NULL,
  ends datetime default NULL,
  visible int(11) default '1',
  type varchar(30) default 'point',
  PRIMARY KEY  (id)
);

CREATE TABLE locations_datasources (
  id int(11) NOT NULL auto_increment,
  datasource_id int(11) default NULL,
  location_id int(11) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE locations_users_tags (
  id int(11) NOT NULL auto_increment,
  location_id int(11) default NULL,
  user_id int(11) default NULL,
  tag_id int(11) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE notes (
  id int(11) NOT NULL auto_increment,
  location_id int(11) default NULL,
  text text NOT NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  user_id int(11) NOT NULL,
  origin varchar(255) NOT NULL default '',
  ranking int(11) default '0',
  visible int(11) default '1',
  type varchar(30) default 'comment',
  PRIMARY KEY  (id)
);

CREATE TABLE project_users (
  id int(11) NOT NULL auto_increment,
  project_id int(11) default NULL,
  user_id int(11) default NULL,
  role varchar(255) NOT NULL default '',
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE projects_points (
  id int(11) NOT NULL auto_increment,
  project_id int(11) default NULL,
  location_id int(11) default NULL,
  PRIMARY KEY  (id)
);

CREATE TABLE tag_namespaces (
  id varchar(64) NOT NULL default '',
  tag_system_id varchar(512) default NULL,
  PRIMARY KEY  (id)
);

CREATE TABLE tags (
  id int(11) NOT NULL auto_increment,
  tag varchar(255) default NULL,
  tag_namespace varchar(64) default NULL,
  PRIMARY KEY  (id)
);

CREATE TABLE users (
  id int(11) NOT NULL auto_increment,
  username varchar(128) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  credentials VARCHAR(256) DEFAULT NULL,
  description VARCHAR (255),
  PRIMARY KEY  (id)
);

CREATE TABLE version (
  id int(11) NOT NULL auto_increment,
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


CREATE TABLE user_profiles (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    prop_key VARCHAR(128),  -- like "mail", "www", etc. - to be defined
    prop_type varchar(128) NOT NULL default 'text',
    prop_value TEXT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE group_users (
  id int(11) NOT NULL auto_increment,
  group_id int(11) default NULL,
  user_id int(11) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

CREATE TABLE groups (
  id int(11) NOT NULL auto_increment,
  groupname varchar(128) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

INSERT INTO groups (groupname) VALUES ('administrators');
INSERT INTO groups (groupname) VALUES ('users');
INSERT INTO groups (groupname) VALUES ('guests');

CREATE TABLE triggers (
  id int(11) NOT NULL auto_increment,
  project_id int(11) default NULL,
  user_id int(11) default NULL,
  trigger_condition varchar(128) default '',  -- to be defined. 'addpoint', etc
  trigger_action text NOT NULL default '',
  adapter varchar(128) default '',
  url varchar(255) NOT NULL default '',
  frequency int(11) default '86400',
  description text,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

INSERT INTO version (version) VALUES ('032-base');
