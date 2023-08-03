# utf-8
import os
from typing import Callable, Union, List
import c4d
import boghma.funfile as funfile


class Singleton:
    """ 单例对象, 只会初始化一次, 所有的实例对象都是同一个对象"""
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}
    def __call__(self, *args, **kwargs):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls(*args, **kwargs)
        return self._instance[self._cls]

class Signal:
    """用于模仿pyqt中的Signal类。"""

    def __init__(self, *args_types, **kwargs_types):
        self._slots = []
    def connect(self, slot: Callable):
        """将槽函数连接到信号上。"""
        if slot not in self._slots:
            self._slots.append(slot)

    def disconnect(self, slot):
        """将槽函数从信号上断开连接。"""
        if slot in self._slots:
            self._slots.remove(slot)

    def emit(self, *args, **kwargs):
        """发送信号，调用所有连接的槽函数。"""
        for slot in self._slots:
            slot(*args, **kwargs)

class CustomSymbolsText: 
    """
    |    方便C4D gedialog ID序列的生成 每个对应的ID可以设置 中文字符和 英文字符, 支持#注释
    |    
    |    文本文件后缀为.cst (custom symbols text),文本形式如下:
    |    -------------------------------------------------------
    |    #起始ID
    |    1000
    |    # 形式：ID名称 /// 中文字符 /// 英文字符 
    |    ID_ANY_A /// 中文 /// en 
    |    ID_ANY_B /// 中文2 /// en2
    |    ID_ANY_C /// 中文3
    |    ID_ANY_D 
    |    
    |    # 可以重改起始ID
    |    2000
    |    ID_ANY /// 中文 /// en
    |    -------------------------------------------------------
    |
    |    在C4D中的使用方式为:
    |
    |        dlg = c4d.GeDialog()
    |        dlg.CST = CustomSymbols(dlg, 'your source_path.cst')
    |    
    |        #上面的步骤做完 dlg.ID_ANY_A 的值就会是 1001
    |        有三种方式可以获取字符：
    |            dlg.CST[1001]  # 直接输入ID号
    |            dlg.CST[dlg.ID_ANY_A]  # 用属性名间接获取ID号
    |            dlg.CST['ID_ANY_A']  # 使用ID名称
    |
    |        可以使用 dlg.switch() 来切换语言 
    
    """
    def __init__(self, host_obj, cst_file_path:str=None):
        assert os.path.exists(cst_file_path), f"cst_file_path not exists. '{cst_file_path}'"
        assert cst_file_path.endswith(".cst"), f"cst_file_path must endswith '.cst'.  not '{cst_file_path}'"
                
        with open(cst_file_path, 'r', encoding='UTF-8') as file:
            self.data = file.read()
        file.close()

        self._host_obj = host_obj
        self._convert_data = {}
        self._convert() 
        self._lan = 0  

    def __getitem__(self, key):
        for id_name, value in self._convert_data.items():
            if isinstance(key, str):
                # 如果传入的是字符 则匹配ID名称
                if id_name == key:
                    if len(value) <= self._lan+1:
                        raise RuntimeError(f"CustomSymbolsText id_name :{id_name} lan out of range")
                    return value[self._lan+1]
            elif isinstance(key, int):
                # 如果传入的是数字 则匹配ID号
                if value[0] == key:
                    if len(value) <= self._lan+1:
                        raise RuntimeError(f"CustomSymbolsText id_name :{id_name} lan out of range")
                    return value[self._lan+1]

    def _convert(self):
        """转换文本内容为对应的对象属性
        """
        self.start = 1000
        for line in self.data.split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # 跳过注释行
            if line[0] == "#":
                continue   
            # 忽略行内注释 
            part = line.split("///")

            if len(part) == 1 and part[0].isdigit():
                self.start = int(part[0].strip())
            else:
                id_name = part.pop(0).strip()
                self._convert_data[id_name] = [self.start+1]
                for str_text in part:
                    self._convert_data[id_name].append(str_text)
                self.start += 1
    
        # add IDs
        for key, data in self._convert_data.items():
            # data = [id, chinese, english]
            setattr(self._host_obj, key, data[0])

    @property
    def lan(self):
        return self._lan
    
    @lan.setter
    def lan(self, value):
        self._lan = max(int(value),0)

    def switch(self):
        """
        切换语言 
        """
        self._lan = int(not self._lan)

    def get_trans(self, first="", second=""):
        return [first, second][self._lan]

class ChatRoom:
    """ 用于dialog间的通信 """
    DEFUALT_CHANNEL = "_WORLD_"

    def __init__(self):
        self.all_listener = []
    
    def check_listener_id(self, listener_id):
        """检查 listener_id 是否合规"""
        if not isinstance(listener_id, (int)):
            error_text = f"type of listener_id must be int, not {type(listener_id)}"
            raise KeyError(error_text)
        
    def add_listener(self, listener_id, action_function):
        """ 新增一个听众 """
        self.check_listener_id(listener_id)
        if self.get_listener(listener_id):
            error_text = f"listener id already exists in chat room! please user other id."
            raise ValueError(error_text)

        listener = {}
        listener["id"] = listener_id
        listener["action"] = action_function
        listener["channel"] = [self.DEFUALT_CHANNEL]
        self.all_listener.append(listener)
    
    def get_listener(self, listener_id):
        """ 通过 id 获取 listener数据"""
        for listener in self.all_listener:
            if listener["id"] == listener_id:
                return listener

    def private_talk_with(self, listener_id, topic=None, msg=None):
        """ 私聊: 只会发送给对应 id 的 listener """
        listener = self.get_listener(listener_id)
        listener["action"](topic, msg)

    # channel
    def check_channel(self, channel):
        """ 检查 channel 是否合规 """
        if not isinstance(channel, (str, int)):
            error_text = f"type of channel must be one of the (str or int), not {type(channel)}"
            raise KeyError(error_text)

    def listen_to_channel(self, listener_id, channel):
        """ 监听 channel, 一个 listener可以监听多个 channel"""
        self.check_channel(channel)
        listener = self.get_listener(listener_id)
        if not listener:
            error_text = f"listener id not exists!"
            raise KeyError(error_text)

        if channel not in listener["channel"]:
            listener["channel"].append(channel)

    def speak_in_channel(self, channel, topic=None, msg=None):
        """ 发送消息: 所有监听 channel 的 listener 都会接受消息 """
        channel = self.check_channel(channel) 
        for listener in self.all_listener:
            if channel in listener["channel"]:
                listener["action"](topic, msg)

class Prefrence: 

    def __init__(self, plugin_path):
        self.plugin_path = plugin_path
        uplevel_dir = os.path.dirname(plugin_path)
        uplevel_name = os.path.basename(uplevel_dir)
        if uplevel_name == "Cinema4d Plugins":
            self.is_dev = False
        elif uplevel_name == "Development":
            self.is_dev = True
        else:
            raise RuntimeError("plugin must under hte Cinema4d Plugins or Development folder")
        self.main_path = os.path.dirname(uplevel_dir)
        self.plugin_name = os.path.basename(plugin_path)
        self.get_plugin_pref_path()
        self.icons_path = self.join("res", "icons")
        self.icons = {}

    def get_info(self):
        info_path = os.path.join(self.plugin_path, "Info.json")
        if os.path.exists(info_path):
            return funfile.read_json(info_path)

    def get_lib_path(self):
        return os.path.join(self.plugin_path, "lib")

    def join(self, *args):
        return f"{self.plugin_path}\\" + "\\".join(args)

    def get_plugin_pref_path(self):
        """
        获取对应插件的resource文件夹
        """
        pref_path = os.path.join(self.main_path, "resource", self.plugin_name)
        funfile.makedirs(pref_path)
        return pref_path

    def get_prefmeta_path(self):
        """
        获取对应插件的matadata.json路径
        """
        HOSTNAME = funfile.gethostname() # 获取当前主机名
        final_path = self.get_plugin_pref_path()
        prefmeta_path = os.path.join(final_path, f"{HOSTNAME}_metadata.json")
        if not os.path.exists(prefmeta_path):
            funfile.write_json(prefmeta_path, {})
        return prefmeta_path

    def set_prefmeta(self, key, val):
        """
        写入对应插件的metadata
        """
        prefmeta_path = self.get_prefmeta_path()
        prefmeta = funfile.read_json(prefmeta_path)
        prefmeta[key] = val 
        funfile.write_json(prefmeta_path, prefmeta)

    def get_prefmeta(self, key):
        """
        写入对应插件的metadata 给定的key属性
        """
        prefmeta_path = self.get_prefmeta_path()
        prefmeta = funfile.read_json(prefmeta_path)
        if key in prefmeta:
            return prefmeta[key] 
        
    def get_icon(self, name):
        
        if name in self.icons:
            return self.icons[name]
        else:
            icon_path_png = os.path.join(self.icons_path, name+".png")
            icon_path_jpg = os.path.join(self.icons_path, name+".jpg")
            if os.path.exists(icon_path_png):
                icon_path = icon_path_png
            elif os.path.exists(icon_path_jpg):
                icon_path = icon_path_jpg 
            else:
                raise RuntimeError(f"get_icon fail: icon not exists. {name}")
            bmp = c4d.bitmaps.BaseBitmap()
            bmp.InitWith(icon_path)
            self.icons[name] = bmp
            return bmp
        
class Logger():
    
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

    def __init__(self):
        self.level = self.DEBUG
        self.msgs = [[0,"LOGGER"]]
    
    def set_level(self, level=0):
        self.level = level
    
    def clean(self):
        self.msgs = [[0,"LOGGER"]]

    def add(self, message="", level=0):
        self.msgs.append([level, str(message)])

    def get(self):
        return self.msgs[-1][1]
    #
    def debug(self, message):
        self.add(message, level=self.DEBUG)
    
    def info(self, message):
        self.add(message, level=self.INFO)
    
    def warning(self, message):
        self.add(message, level=self.WARNING)
    
    def error(self, message):
        self.add(message, level=self.ERROR)
    
    def critical(self, message):
        self.add(message, level=self.CRITICAL)

    