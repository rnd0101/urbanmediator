import sys
import os
import appuifw
import series60_console
import e32

def query_and_exec():
    
    def is_py(x):
        ext=os.path.splitext(x)[1].lower()
        return ext == '.py' or ext == '.pyc' or ext == '.pyo'
    script_list = []
    for nickname,path in script_dirs:
        if os.path.exists(path):
            script_list += map(lambda x: (nickname+x,path+'\\'+x),\
                               filter(is_py, os.listdir(path)))
           
    index = appuifw.selection_list(map(lambda x: unicode(x[0]), script_list))
    if index >= 0:
        execfile(script_list[index][1], globals())

def exec_interactive():
    import interactive_console
    interactive_console.Py_console(my_console).interactive_loop()

def exec_btconsole():
    import btconsole
    btconsole.main()

def icing():
    import loc

def menu_action(f):
    appuifw.app.menu = []
    saved_exit_key_handler = appuifw.app.exit_key_handler

    try:
        try:
            f()
        finally:
            appuifw.app.exit_key_handler = saved_exit_key_handler
            appuifw.app.title = u'Python'
            init_options_menu()
            appuifw.app.body = my_console.text
            appuifw.app.screen='normal'
            sys.stderr = sys.stdout = my_console
    except:
        import traceback
        traceback.print_exc()

def init_options_menu():
    appuifw.app.menu = [
                        (u"Icing",\
                         lambda: menu_action(icing)),
                        (u"Run script",\
                         lambda: menu_action(query_and_exec)),
                        (u"Interactive console",\
                         lambda: menu_action(exec_interactive)),\
                        (u"Bluetooth console",\
                         lambda: menu_action(exec_btconsole)),\
                        (u"About Python",\
                         lambda: appuifw.note(u"See www.python.org for more information.", "info"))]
if(e32.s60_version_info>=(3,0)):
    script_dirs = [(u'c:',u'c:\\python'),
                   (u'e:',u'e:\\python')]
    for path in (u'c:\\python\\lib',u'e:\\python\\lib'):
        if os.path.exists(path):
            sys.path.append(path)
else:
    scriptshell_dir = os.path.split(appuifw.app.full_name())[0]
    script_dirs = [(u'', scriptshell_dir),
                   (u'my\\', scriptshell_dir+'\\my')]
my_console = series60_console.Console()
appuifw.app.body = my_console.text
sys.stderr = sys.stdout = my_console
from e32 import _stdo
_stdo(u'c:\\python_error.log')         # low-level error output
init_options_menu()
print str(copyright)+"\nVersion "+e32.pys60_version


