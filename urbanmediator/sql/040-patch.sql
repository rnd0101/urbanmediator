ALTER TABLE projects_points ADD visible int(11) default '1';

UPDATE projects_points AS pp, locations AS l 
    SET pp.visible = 0 
    WHERE pp.location_id = l.id AND l.visible = 0;

INSERT INTO version (version) VALUES ('040-patch');
