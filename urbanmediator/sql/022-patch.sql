
CREATE TABLE projects_points (
    id INT NOT NULL AUTO_INCREMENT,
    project_id INT,   -- = location_id
    location_id INT,  -- = location_id
    PRIMARY KEY (id)
);

INSERT INTO version (version) VALUES ('022-patch');
