
import os
import sys
import importlib

try:
    import c4d
    import maxon
except:
    pass


ENABLE_ASSERT_DIALOG = False

def AssertDialog(fn):
    # 定义一个嵌套函数
    def assert_dlg(*args,**kwargs):
        try:
            res = fn(*args,**kwargs)
        except Exception as err:
            if ENABLE_ASSERT_DIALOG:
                c4d.gui.MessageDialog(err)
            raise 
        return res
    return assert_dlg

def blog(*args,**kwargs):
    try:
        message = ""
        sep = " "
        if "sep" in kwargs:
            sep = kwargs["sep"]
        for arg in args:
            message += str(arg) +sep
        if sep != "":
            message = message[:-1]
        logger = maxon.Loggers.Get("net.boghma.logger")
        logger.Write(maxon.TARGETAUDIENCE.ALL, message.format(logger.GetName()), maxon.MAXON_SOURCE_LOCATION(0), maxon.WRITEMETA.DEFAULT)
    except Exception as e:
        print(*args,**kwargs)


def iter_import(name="boghma.", path=""):
    for file in os.listdir(path):
        if file[0] == "_" or not file.endswith(".py"):
            continue
        modname = file.split(".")[0]
        mod_obj = importlib.import_module(name+modname)
        importlib.reload(mod_obj)   

lib_Path, f = os.path.split(__file__)
if lib_Path not in sys.path:
	sys.path.insert(0,lib_Path)
iter_import("boghma.", lib_Path)

# ualib
lib_Path = os.path.join(lib_Path, "ualib")
if lib_Path not in sys.path:
    sys.path.insert(0,lib_Path)

import ualib
importlib.reload(ualib)  
iter_import("ualib.", lib_Path)






