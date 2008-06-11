As we plan to modify the database schema is often as needed, we need some
kind of convention to access (and convert between) different versions of the 
schema. Here's the simplest way we could come up with.

File name naming conventions used for the database schema are

    <#>-base.sql
    
and

    <#>-patch.sql
    
where <#> is a running number with three digits (e.g. 007). Base files contain
a full schema definition, i.e. CREATE statements. Patch files usually contain 
ALTER statements.


Each patch or base should contain this at the end:

    INSERT INTO version (version) VALUES ('NNN-patch');

or 

    INSERT INTO version (version) VALUES ('NNN-base');

where NNN is the running number mentioned above.

For example with

    001-base.sql
    002-patch.sql
    003-patch.sql
    004-patch.sql
    005-base.sql
    006-patch.sql
    007-base.sql

The latest database instance can be created by running "007-base.sql" - or 
alternatively by running "001-base.sql" and then all of the patch files in
the given order. If the database is currently in state "005-base.sql", then 
the schema can be converted to its latest state by running "006-patch.sql".

To apply patch:

    mysql ... < NNN-patch.sql

To setup tables in the database:

    mysql ... < NNN-base.sql

To check the version of the database, run version.sql:

    mysql ... < version.sql

where "..." is specific to the database.

