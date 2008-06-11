ALTER TABLE notes ADD ord int(11) default '0';
ALTER TABLE locations ADD ord int(11) default '0';
ALTER TABLE triggers ADD ord int(11) default '0';

INSERT INTO version (version) VALUES ('041-patch');
