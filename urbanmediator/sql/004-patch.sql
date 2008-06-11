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

CREATE TABLE locations_users_tags (
    id INT NOT NULL AUTO_INCREMENT,
    location_id INT,
    tag_id INT,
    user_id INT,
    added TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
