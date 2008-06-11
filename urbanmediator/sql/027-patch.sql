
# fixing typo
ALTER TABLE user_profiles CHANGE prep_key prop_key VARCHAR(128);

CREATE TABLE groups (
  id int(11) NOT NULL auto_increment,
  groupname varchar(128) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);

INSERT INTO groups (groupname) VALUES ('administrators');
INSERT INTO groups (groupname) VALUES ('users');
INSERT INTO groups (groupname) VALUES ('guests');

INSERT INTO version (version) VALUES ('027-patch');
