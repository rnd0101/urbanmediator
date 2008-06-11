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

