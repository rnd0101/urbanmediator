CREATE TABLE locations (
    id INT NOT NULL AUTO_INCREMENT,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    title VARCHAR(64),
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    origin VARCHAR(255) NOT NULL DEFAULT '',
    ranking INT DEFAULT 0,
    url VARCHAR(255) NOT NULL DEFAULT '',
    PRIMARY KEY (id)
);

CREATE TABLE notes (
    id INT NOT NULL AUTO_INCREMENT,
    location_id INT,
    text TEXT NOT NULL,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    origin VARCHAR(255) NOT NULL DEFAULT '',
    ranking INT DEFAULT 0,
    PRIMARY KEY (id)
);

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(128),
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

CREATE TABLE tags (
    id INT NOT NULL AUTO_INCREMENT,
    tag VARCHAR(255),
    tag_namespace VARCHAR(64),
    PRIMARY KEY (id)
);

CREATE TABLE tag_namespaces (
    id VARCHAR(64),
    tag_system_id VARCHAR(512),
    PRIMARY KEY (id)
);

DELETE FROM tag_namespaces WHERE id = '';
INSERT INTO tag_namespaces (id, tag_system_id) VALUES
    ('', 'http://icing.arki.uiah.fi/');
INSERT INTO tag_namespaces (id, tag_system_id) VALUES
    ('official', 'http://official.icing.arki.uiah.fi/');


CREATE TABLE locations_users_tags (
    id INT NOT NULL AUTO_INCREMENT,
    location_id INT,
    user_id INT,
    tag_id INT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
CREATE TABLE project_users (
    id INT NOT NULL AUTO_INCREMENT,
    project_id INT,   -- = location_id
    user_id INT,
    role VARCHAR(255) NOT NULL DEFAULT '',
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

ALTER TABLE locations ADD uuid VARCHAR(2048) NOT NULL DEFAULT '';
UPDATE locations set uuid = id where uuid='';
ALTER TABLE locations ADD begins DATETIME DEFAULT NULL;
ALTER TABLE locations ADD expires DATETIME DEFAULT NULL;
ALTER TABLE locations ADD ends DATETIME DEFAULT NULL;
ALTER TABLE locations ADD visible INT DEFAULT 1;
ALTER TABLE locations ADD type VARCHAR (30) DEFAULT 'point'; -- 'project'
ALTER TABLE locations MODIFY title VARCHAR (255);

ALTER TABLE notes ADD visible INT DEFAULT 1;
ALTER TABLE notes ADD type VARCHAR (30) DEFAULT 'comment';

CREATE TABLE locations_datasources (
    id INT NOT NULL AUTO_INCREMENT,
    datasource_id INT DEFAULT NULL,
    location_id INT,
    uuid VARCHAR(255) NOT NULL DEFAULT '',
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY (uuid)
);

CREATE TABLE datasources (
    id INT NOT NULL AUTO_INCREMENT,
    type VARCHAR (30) DEFAULT '', -- "feed", "scrape", "api query", etc
    adapter VARCHAR (128) DEFAULT '', -- module used to fetch, like specific scraper
    url VARCHAR(255) NOT NULL DEFAULT '',
    frequency INT DEFAULT 86400,     -- how frequently fetched, s
    description TEXT,  -- human readable description
    private INT DEFAULT 0, -- True/False
    credentials VARCHAR(255) NOT NULL DEFAULT '', -- to access the resource
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);


update locations set visible = 0 where ranking < -199;
update notes set visible = 0 where ranking < -199;

drop table locations_datasources;

CREATE TABLE locations_datasources (
    id INT NOT NULL AUTO_INCREMENT,
    datasource_id INT DEFAULT NULL,
    location_id INT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
CREATE TABLE version (
    id INT NOT NULL AUTO_INCREMENT,
    version VARCHAR(100),
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

INSERT INTO version (version) VALUES ('021-patch');

CREATE TABLE projects_points (
    id INT NOT NULL AUTO_INCREMENT,
    project_id INT,   -- = location_id
    location_id INT,  -- = location_id
    PRIMARY KEY (id)
);

INSERT INTO version (version) VALUES ('022-patch');

DELETE FROM tag_namespaces WHERE id = 'category';
INSERT INTO tag_namespaces (id, tag_system_id) VALUES
    ('category', 'http://category.icing.arki.uiah.fi');

INSERT INTO version (version) VALUES ('023-patch');

INSERT INTO version (version) VALUES ('024-base');
