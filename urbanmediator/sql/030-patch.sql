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

INSERT INTO version (version) VALUES ('030-patch');
