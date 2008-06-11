
DELETE FROM tag_namespaces WHERE id = 'status';
INSERT INTO tag_namespaces (id, tag_system_id) VALUES
    ('status', 'http://issuereporter.icing.arki.uiah.fi');

INSERT INTO version (version) VALUES ('031-patch');
