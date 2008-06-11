
ALTER TABLE users ADD credentials VARCHAR(256) DEFAULT NULL;

CREATE TABLE user_profiles (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT,
    prep_key VARCHAR(128),  -- like "mail", "www", etc. - to be defined
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

INSERT INTO version (version) VALUES ('026-patch');
