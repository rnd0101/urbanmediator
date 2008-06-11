
DELETE FROM tag_namespaces WHERE id = 'category';
INSERT INTO tag_namespaces (id, tag_system_id) VALUES
    ('category', 'http://category.icing.arki.uiah.fi');

INSERT INTO version (version) VALUES ('023-patch');
