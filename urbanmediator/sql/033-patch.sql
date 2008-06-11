CREATE TABLE locations_policy_table (
  id int(11) NOT NULL auto_increment,
  location_id int(11) default NULL,
  user_id int(11) default NULL,
  role varchar(255) NOT NULL default '',
  adder_user_id int(11) default NULL,
  added timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (id)
);

INSERT INTO version (version) VALUES ('033-patch');
