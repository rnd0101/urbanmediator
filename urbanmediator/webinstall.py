# -*- coding: utf-8 -*-

"""
    This file is part of Urban Mediator software.

    Copyright (c) 2008 University of Art and Design Helsinki
    See the file LICENSE.txt for copying permission.

    Controller for the Web Installer.
"""

import os, sys

instance_dir = os.getcwd()

try:
    import web
    from web.utils import Storage
    from web import form
except ImportError:
    print "Please install web.py first!"
    sys.exit(1)

render = web.template.render('templates/install/', cache=True)

def get_page(template_name, context, *args, **kwargs):
    context.setdefault("title", "UM SETUP")
    page = getattr(render, template_name)
    print render.base( page(context, cache=True, *args, **kwargs), context, cache=True )

import i18n

_ = i18n._


urls = (
    '/', 'Index',
    '/setupdb', 'SetupDB',
)

LOCAL_DIR_NAME = os.path.join(instance_dir, "local")
LOCAL_CONFIG_FILE_NAME = os.path.join(LOCAL_DIR_NAME, "config.py")

web.webapi.internalerror = web.debugerror

def check_prereqs():
    missing = []

    try:
        try:
            import elementtree.ElementTree as et
        except ImportError:
            # Python >= 2.5.1 ?
            import xml.etree.ElementTree as et
    except: missing.append("elementtree")

    try: import MySQLdb
    except: missing.append("MySQLdb")

    try: import Image
    except: missing.append("PIL")
    return missing

class Index:
    def GET(self):
        try:
            cfg_locals = {}
            execfile(LOCAL_CONFIG_FILE_NAME, globals(), cfg_locals)  # local config overrides
        except IOError:
            print LOCAL_CONFIG_FILE_NAME ," not found"
        except:
            raise
            print "ERROR reading config"

        missing_prereqs = check_prereqs()

        if missing_prereqs:
            print "Please install missing software first:"
            print ", ".join(missing_prereqs)
            return

        if "db_parameters" not in cfg_locals:
            form = setup_db_form()
            context = Storage(title=_("Setting database"),
                          description=_("Enter some values to start with the database setup"))
            get_page("setupdb", context, form)
            return

        if "autoconfigured" in cfg_locals:
            print "Already autoconfigured. Edit ", LOCAL_CONFIG_FILE_NAME

        print "This instance seems to be configured. Revise ", LOCAL_CONFIG_FILE_NAME

setup_db_form = form.Form( 
    form.Textbox("host",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="Host of db",
        value="""localhost""",
    ), 
    form.Textbox("user",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="MySQL root user",
        value="""root""",
    ), 
    form.Password("passwd",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="MySQL root user password",
        value="",
    ), 
    form.Textbox("db",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="Database",
        value="""mysql""",
        post="<hr>",
    ), 

    form.Textbox("dbuser",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="Desired database user",
        value="""um""",
        pre="<hr>",
    ), 

    form.Password("passwd1",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="DB user password",
        value="",
    ), 

    form.Password("passwd2",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="DB user password (repeat)",
        value="",
    ), 

    form.Textbox("dbname",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="Desired database name",
        value="""um""",
    ),

    form.Textbox("port",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="Desired port to run webserver",
        value="""9080""",
        pre="<hr>",
    ),

    form.Textbox("ip",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="Desired interface (IP) to run webserver (usually: 0.0.0.0 or 127.0.0.1)",
        value="""0.0.0.0""",
        pre="<hr>",
    ),

    form.Textbox("root_url",
        form.Validator('Must be filled', lambda x:x.strip()),
        description="Root URL (no trailing slash!), e.g. http://my.um.servers.org/example",
        value="""http://localhost:9080""",
        pre="<hr>",
    ),


#    validators = [form.Validator("Passwords didn't match.", 
#        lambda i: i.passwd1 == i.passwd2)]
) 



def create_dbs(i):
    q1 = """
    create user '$user'@'localhost' identified by '$passw';
    create database $dbname;
    use $dbname;
    GRANT ALL PRIVILEGES ON *.* TO '$user'@'localhost';
    """

    import MySQLdb 
    from string import Template

    q1t = Template(q1)
    query1 = q1t.substitute(user=i.dbuser, passw=i.passwd1, dbname=i.dbname)

    try:
        conn = MySQLdb.connect (host = i.host,
                           user = i.user,
                           passwd = i.passwd,
                           db = i.db)
        cursor = conn.cursor ()
        #cursor.execute ("SELECT VERSION()")   
        #row = cursor.fetchone ()
        #print "server version:", row[0]
        #cursor.close ()

        cursor.execute (query1)   
        row = cursor.fetchone ()
        cursor.close()
        conn.close ()
    except:
        raise
        print "Database operation failed. Maybe user or database already exists? Or root user name/password wrong"
        return

    c0 = """\nautoconfigured = 1"""
    c1 = """\ndb_parameters = dict(dbn='$db', db='$dbname', user='$dbuser', pw='$passwd1', use_unicode=False)
    \nlisten_ip_port = "$ip:$port"
    \nadmin_credentials = [{
    'username': '$dbuser@admin',
    'password': '$passwd1',
    },]
    \nbase_url = "$root_url"
    \nschema_base_url = base_url + "/Static"

    """

    try:
        print "\nAdmin user: %(dbuser)s@admin and same password as that of database user." % i
    except:
        print "\nSee local/config.py for admin user credentials"

    try:
        os.mkdir(LOCAL_DIR_NAME)
    except:
        pass

    try:
        fc = open(LOCAL_CONFIG_FILE_NAME, "a")
        fc.write(c0)
        fc.write(Template(c1).substitute(**i))
        fc.close()
    except:
        print "cant write to %s : add the following manually" % LOCAL_CONFIG_FILE_NAME
        print Template(c1).substitute(**i)

    # creating tables
    try:
        files = "sql/042-base.sql",
        for f in files:
            phase = "connection not established at file " + f
            conn = MySQLdb.connect(host = i.host,
                           user = i.dbuser,
                           passwd = i.passwd1,
                           db = i.dbname)
            cursor = conn.cursor ()
            phase = "reading file " + f
            cursor.execute(open(f).read())
#            cursor.execute("SELECT VERSION();")
            #row = cursor.fetchone ()
            #print row
            try:
                cursor.close()
            except:
                pass
            phase = "closing connection after file " + f
            conn.close ()
    except:
        raise
        print "Database operation failed at ", phase
        return 0
        
    return 1


class SetupDB:
    def GET(self):
        form = setup_db_form()
        context = Storage(title=_("Setting database"),
                          description=_("Enter some values to start with the database setup"))
        get_page("setupdb", context, form)

    def POST(self): 
        form = setup_db_form()
        if not form.validates() or form.d.passwd1 != form.d.passwd2:
            context = Storage(title=_("Setting database"),
                          description=_("Enter some values to start with the database setup"))
            get_page("setupdb", context, form)
            return
        else:
            res = create_dbs(form.d)
            if res:
                print "Database and tables creation done"

web.template.Template.globals.update(dict(
  ctx = web.ctx,
  _ = i18n._,
  LANG = i18n.getLanguage,
  enumerate = enumerate
))

LISTEN_AT = "127.0.0.1:9080"
LISTEN_AT = "0.0.0.0:9080"

def main():
    import urbanmediator
    os.chdir(os.path.dirname(urbanmediator.__file__))  #!!!

    if len(sys.argv) == 1:
        try:
            sys.argv[1] = LISTEN_AT
        except:
            sys.argv.insert(1, LISTEN_AT)
    web.run(urls, globals())

if __name__ == "__main__":
    main()
