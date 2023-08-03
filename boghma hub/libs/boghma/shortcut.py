# -*- coding: utf-8 -*-  

# Develop for Maxon Cinema 4D version 2023.1.0
#   ++> Custom Cinema 4D Shortcut Functions

###  ==========  Copyrights  ==========  ###

"""
    Copyright [2023] [DunHouGo]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

###  ==========  Author INFO  ==========  ###
__author__ = "DunHouGo"
__copyright__ = "Copyright (C) 2023 Boghma"
__license__ = "Apache-2.0 License"
__version__ = "2023.0.0"
###  ==========  Import Libs  ==========  ###
import c4d
import typing
from typing import Optional
#=============================================
#                  介绍 Intro
#=============================================
"""
如何在Cinema 4D中查找和删除快捷方式。

在C4D内部,快捷键通过shortcut sequence绑定,通过input events侦测.


#! keySequence: 键盘输入序列, e.g., [c4d.QUALIFIER_SHIFT, '1'].

#keySequence : e.g.

    [c4d.QUALIFIER_SHIFT, c4d.QUALIFIER_ALT, "S", "T"]

对应快捷键为 SHIFT + ALT + S ~ T.

内部运算逻辑为:
    1.所有修饰键 或 在一起 (ORed) or sum
    2.支持多重连续按键 , 比如 M~S
所以 SHIFT + ALT + S ~ T 的实际数值对应为 
    [1, 4, "S", "T"]
换算为
    [(5,83),(84)]
运算为    
[  (5, 83),     # (qualifier = 1 | 4 = 5, key = ASCII_VALUE("S"))
    (84)        # (qualifier = 0        , key = ASCII_VALUE("T") ]
    
ord(): str => ASCII


#! Shortcut bc (c4d.BaseContainer): 快捷键容器结构.

#   Container Access             ID     Description
#   bc[0]                          0    第一个key stroke(修饰键序列).
#   bc[1]                          1    第一个key stroke(ASCII键值).

#   bc[10]                        10    key stroke(修饰键序列)(可选).
#   bc[11]                        11    第一个key stroke(ASCII键值)(可选).
#   [...]
#   bc[990]                      990    最大[99]key stroke(修饰键序列)(可选).
#   bc[991]                      991    最大[99]key stroke(ASCII键值)(可选).

#   bc[c4d.SHORTCUT_PLUGINID]   1000    插件ID.
#   bc[c4d.SHORTCUT_ADDRESS]    1001    指定语境(生效管理器).
#   bc[c4d.SHORTCUT_OPTIONMODE] 1002    是否打开选项.

对于多重快捷键,e.g., M ~ S, 每个index都乘10, 也就是范围[0,990], 共99个.

示例一:
    按键为 "0" .
        1."0"的ASCII编码为48.
        2.没有修饰键
        #   0: 0
        #   1: 48
        #   1000: 200000084 # pID
        #   1001: 0
        #   1002: 0    

示例二:
    按键为 "M~S" .
        1."M"的ASCII编码为77.
        2."S"的ASCII编码为83.
        3.没有修饰键
        #   0: 0
        #   1: 48
        #   1000: 200000084 # pID
        #   1001: 0
        #   1002: 0 

#! strokeData (list): 由修饰键+Key组成的元组列表

strokeData: list[tuple[int, int]]
"""

# Windows ID
# 这些ID是没有地方能查询到的, 唯一获取途径是通过4.FindShortcutAssign，指认到管理器后查询。
# 这里罗列出一些常用ID
OBJECT_MANAGER: int = 100004709
MATERIAL_MANAGER: int = 150041
TIMELINE_MANAGER: int = 465001516
LAYER_MANAGER: int = 100004704
NODEEDITOR_MANAGER: int = 465002211
ATTRIBUTTE_MANAGER: int = 1000468
ASSET_BROWSER: int = 1054225
PICTURE_VIEWER: int = 430000700
PROJECT_ASSET_INSPECTOR : int = 1029486
TAKE_MANAGER: int = 431000053
RENDER_QUEUE: int = 465003500
RENDER_SETTING: int = 12161

#=============================================
#                    Class
#=============================================
""" 
#! keySequence:  list[typing.Union[int, str]]
#! 键盘输入序列列表, e.g., [c4d.QUALIFIER_SHIFT, '1'] , [4,'2'] , [0, 'Y']

1.获取插件快捷键列表
2.获取快捷键序号(序号,不存在时返回False)
3.删除快捷键
4.获取快捷键指认的插件id和管理器id
5.添加快捷键到对应的插件id和管理器id(可选)
6.KeySequence转换StrokeData
7.检测快捷键是否已经绑定给指定插件
8.为插件添加快捷键(监测快捷键指认)
9.打印index信息
"""
class ShortCut():
    # 0.init function
    def __init__(self) -> None:
        # print("Custom shortcut library import success!")
        pass
    # _ 辅助：输入同时执行
    def check_special_input(self,QUALIFIER:int, key:str):
        bc: c4d.BaseContainer = c4d.BaseContainer()
         # Querying for a specific key with GetInputState.
         
        # Note that you must poll for upper case characters, e.g., X instead of x.
        if not c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD, ord (key.upper()), bc):
            raise RuntimeError("Failed to query input events.")
        # Test if the queried key is indeed being pressed.
        print (f"{bc[c4d.BFM_INPUT_VALUE] == 1 = }")
        # Test if this did co-occur with a CTRL button press.
        print (f"{bc[c4d.BFM_INPUT_QUALIFIER] == QUALIFIER = }")
    # _ 辅助：执行时输入
    def check_input_state(self):
        bc: c4d.BaseContainer = c4d.BaseContainer()
        # Querying for a specific key with GetInputState.

        if not c4d.gui.GetInputEvent(c4d.BFM_INPUT_KEYBOARD, bc):
            raise RuntimeError("Failed to query input events.")

        # Get the key which is currently be pressed as an ASCII value.
        print (f"{bc[c4d.BFM_INPUT_CHANNEL] = } ({chr (bc[c4d.BFM_INPUT_CHANNEL])})")
        # We can still read all the other things which are written into an input event container, as
        # for example a modifier key state.
        print (f"{bc[c4d.BFM_INPUT_QUALIFIER]}")  
    # 获取快捷键
    # 1.获取插件快捷键元组列表
    def GetPluginShortcuts(self, pluginID: int , print_console: bool = False) -> list[list[tuple[int]]]:
        """Retrieves the shortcuts for a plugin-id.

        Args:
            pid (int): The plugin id.

        Returns:
            list[list[tuple[int]]]: The shortcut sequences for the plugin.
        """
        # Get all shortcut containers for the plugin id.
        count = c4d.gui.GetShortcutCount()
        matches = [c4d.gui.GetShortcut(i) for i in range(count)
                    if c4d.gui.GetShortcut(i)[c4d.SHORTCUT_PLUGINID] == pluginID]

        # build the shortcut data.
        result = []
        for item in matches:
            sequence = []
            for i in range(0, c4d.SHORTCUT_PLUGINID, 10):
                a, b = item[i], item[i+1]
                if isinstance(a, (int, float)):
                    sequence.append((a, b))

            if sequence != []:
                result.append(sequence)
        if print_console == True:
        # Output in console
            print("---------------")
            print("Plugin Name : {}".format(c4d.plugins.FindPlugin(pluginID).GetName()))             
            for item in result:
                for a, b in item:
                    
                    print (a, c4d.gui.Shortcut2String(a, b))
            print("---------------")
        if result == []:
            result = None
        return result
    # 2.获取快捷键全局序号(序号,不存在时返回False)
    def CheckShortcurIndex(self, keySequence: list[typing.Union[int, str]], 
                    managerId: typing.Optional[int] = None,
                    pluginId: typing.Optional[int] = None) -> bool:
        """
        Finds a shortcut index by the given #keySequence and optionally #managerId and/or #pluginId.
        False if shortcut didn't matched
            
        Args:
            keySequence: A sequence of keyboard inputs, e.g., [c4d.QUALIFIER_SHIFT, '1'].
            managerId (optional): The manager context of the shortcut to find or remove.
            pluginId (optional): The plugin ID of the plugin invoked by the shortcut.
        
        Returns:
            The success of the removal operation.

        Raises:
            RuntimeError: On illegal key symbols.
            RuntimeError: On non-existing shortcut key sequences.
        """
        # The list of key stroke modifier-key tuples.
        strokeData: list[tuple[int, int]] = []
        # A variable to OR together the qualifiers for the current key stroke.
        currentModifiers: int = 0

        #todo 获取 [strokeData]  
        #todo 转换keySequence:[c4d.QUALIFIER_SHIFT, '1'] => Output [(1, 49)]
        for key in keySequence:
            # Modifier key sequence, e.g., SHIFT + ALT + CTRL
            if isinstance(key, (int, float)):
                currentModifiers |= key
            # Character.
            elif isinstance(key, str) and len(key) == 1:
                strokeData.append((currentModifiers, ord(key.upper())))
                currentModifiers = 0
            # Errors
            else:
                raise RuntimeError(f"Found illegal key symbol: {key}")
        
        #todo Get the shortcut at #index.
        # Iterate over all shortcuts in Cinema 4D.
        for index in range(c4d.gui.GetShortcutCount()):
            
            bc: c4d.BaseContainer = c4d.gui.GetShortcut(index)

            # if #strokeData matches #bc.
            isMatch: bool = True
            for i, (qualifier, key) in enumerate(strokeData):
                idQualifier: int = i * 10 + 0
                idKey: int = i * 10 + 1
                # A qualifier + key stroke did not match, we break out.
                #? C4D中不存在此快捷键
                if bc[idQualifier] != qualifier or bc[idKey] != key:
                    isMatch = False
                    break
            
            # Something in the key sequence did not match with #strokeData, so we try the next shortcut
            # container provided by the outer loop.
            if not isMatch:
                continue
            
            # We could do here some additional tests, as shortcut key strokes do not have to be unique,
            # i.e., there could be two short-cuts "Shift + 1" bound to different manager contexts.
            if pluginId is not None and bc[c4d.SHORTCUT_PLUGINID] != pluginId:
                continue
            if managerId is not None and bc[c4d.SHORTCUT_ADDRESS] != managerId:
                continue
            
            # All tests succeeded, the shortcut at the current index should be removed, we instead just
            # return the index to make this example a bit less volatile.

            # return c4d.gui.RemoveShortcut(index)
            return index

        # All shortcuts have been traversed and no match was found, the user provided a key sequence
        # which is not a shortcut.
        return False
    # 3.删除快捷键    
    def RemoveShortcut(self,keySequence: list[typing.Union[int, str]], 
                    managerId: typing.Optional[int] = None,
                    pluginId: typing.Optional[int] = None) -> bool:
        """
        Remove Shortcut by given qualifier and key    
            
        Args:
            qualifier (int): modifier key 
            key (int): ascii code of key
        """
        index = self.CheckShortcurIndex(keySequence,managerId,pluginId)
        
        try:
            if index:
                c4d.gui.RemoveShortcut(index)
        except:
            print ("Shortcut Remove Failed")
            return False   
    # 4.获取快捷键指认的插件id和管理器id
    def FindShortcutAssign(self,keySequence: list[typing.Union[int, str]],managerId: typing.Optional[int] = None,pluginId: typing.Optional[int] = None) -> bool:
        """
        Finds a shortcut assigned plugin id and name
            
        Args:
            keySequence: A sequence of keyboard inputs, e.g., [c4d.QUALIFIER_SHIFT, '1'].
        
        Returns:
            The plugin id.
            The plugin name.
            
        Raises:
            RuntimeError: On illegal key symbols.
            RuntimeError: On non-existing shortcut key sequences.
        """
        # The list of key stroke modifier-key tuples.
        strokeData: list[tuple[int, int]] = []
        # A variable to OR together the qualifiers for the current key stroke.
        currentModifiers: int = 0

        #todo 获取 [strokeData]  
        #todo 转换keySequence:[c4d.QUALIFIER_SHIFT, '1'] => Output [(1, 49)]
        for key in keySequence:
            # Extend a modifier key sequence, e.g., SHIFT + ALT + CTRL
            if isinstance(key, (int, float)):
                currentModifiers |= key
            # A character key was found, append an input event.
            elif isinstance(key, str) and len(key) == 1:
                strokeData.append((currentModifiers, ord(key.upper())))
                currentModifiers = 0
            # Something else was found, yikes :)
            else:
                raise RuntimeError(f"Found illegal key symbol: {key}")
        
        #todo Get the shortcut at #index.
        # Now we can iterate over all shortcuts in Cinema 4D.
        for index in range(c4d.gui.GetShortcutCount()):            
            bc: c4d.BaseContainer = c4d.gui.GetShortcut(index)
            # We test if #strokeData matches #bc.
            isMatch: bool = True
            for i, (qualifier, key) in enumerate(strokeData):
                idQualifier: int = i * 10 + 0
                idKey: int = i * 10 + 1
                # A qualifier + key stroke did not match, we break out.
                #? C4D中不存在此快捷键
                if bc[idQualifier] != qualifier or bc[idKey] != key:
                    isMatch = False
                    break
            if not isMatch:
                continue

            pluginId = bc[c4d.SHORTCUT_PLUGINID]
            managerId = bc[c4d.SHORTCUT_ADDRESS]
            return pluginId,managerId
        return False
    # 5.添加快捷键到对应的插件id和管理器id(可选)     
    def AddShortCut(self,keySequence: list[typing.Union[int, str]], 
                    pluginId,
                    managerId: typing.Optional[int] = 0,
                    ) -> bool:
        """
        Add Shortcut by given qualifier and key to given ID  
            
        Args:
            qualifier (int): modifier key 
            key (int): ascii code of key
            pluginID (int): plugin ID
        """
        # The list of key stroke modifier-key tuples.
        strokeData: list[tuple[int, int]] = []
        # A variable to OR together the qualifiers for the current key stroke.
        currentModifiers: int = 0
            
        for key in keySequence:
            # Extend a modifier key sequence, e.g., SHIFT + ALT + CTRL
            if isinstance(key, (int, float)):
                currentModifiers |= key
            # A character key was found, append an input event.
            elif isinstance(key, str) and len(key) == 1:
                #strokeData.append((currentModifiers, ord(key.upper())))
                qualifier = currentModifiers
                key = ord(key.upper())
                currentModifiers = 0
            # Something else was found, yikes :)
            else:
                raise RuntimeError(f"Found illegal key symbol: {key}")
        
        for x in range(c4d.gui.GetShortcutCount()):
            shortcutBc = c4d.gui.GetShortcut(x)
            # Check if shortcut is stored in the basecontainer.        
            if shortcutBc[0] == qualifier and shortcutBc[1] == key:
                if shortcutBc[c4d.SHORTCUT_PLUGINID] == pluginId:
                    print ("Shortcut {} is already Used for Command ID: {}".format(c4d.gui.Shortcut2String(qualifier, key), shortcutBc[c4d.SHORTCUT_PLUGINID]))
                    return
            
        # Define shortcut container
        bc = c4d.BaseContainer()
        bc.SetInt32(c4d.SHORTCUT_PLUGINID, pluginId)
        bc.SetLong(c4d.SHORTCUT_ADDRESS, managerId)
        bc.SetLong(c4d.SHORTCUT_OPTIONMODE, 0)
        # User defined key
        bc.SetLong(0, qualifier)
        bc.SetLong(1, key)
        if c4d.gui.AddShortcut(bc):
            print("Shortcut Installed Susessful")
        return True
    # 6.KeySequence转换StrokeData
    #   ++》[c4d.QUALIFIER_SHIFT, '1'] => Output [(1, 49)]
    def KeySequencetoStrokeData(self,keySequence: list[typing.Union[int, str]]):
        """
        Convert Example: 
        1.[c4d.QUALIFIER_SHIFT, '1'] => Output [(1, 49)]
        2.[c4d.QUALIFIER_SHIFT, c4d.QUALIFIER_ALT, "S", "T"] => Output [(5,83),(0,84)]

        Alt : c4d.QUALIFIER_ALT = 4
        
        Ctrl : c4d.QUALIFIER_CTRL = 2
        
        Shift : c4d.QUALIFIER_SHIFT = 1

        Returns:
            _type_: _description_
        """
        strokeData: list[tuple[int, int]] = []
        # A variable to OR together the qualifiers for the current key stroke.
        currentModifiers: int = 0

        #todo 获取 [strokeData]
        #todo 转换keySequence:[c4d.QUALIFIER_SHIFT, '1'] => Output [(1, 49)]
        for key in keySequence:
            # Extend a modifier key sequence, e.g., SHIFT + ALT + CTRL
            if isinstance(key, (int, float)):
                currentModifiers |= key
            # A character key was found, append an input event.
            elif isinstance(key, str) and len(key) == 1:
                strokeData.append((currentModifiers, ord(key.upper())))
                currentModifiers = 0
            # Something else was found, yikes :)
            else:
                raise RuntimeError(f"Found illegal key symbol: {key}")
        return strokeData
    # 7.检测快捷键是否已经绑定给指定插件
    def PluginhasShortcut(self, keySequence: list[typing.Union[int, str]], pluginId:int):
        """Check if shortcut binding with given plugin
        Args:
            keySequence: A sequence of keyboard inputs, e.g., [c4d.QUALIFIER_SHIFT, '1'].            
            pluginId (optional): The plugin ID of the plugin invoked by the shortcut.

        Returns:
            bool: True if Shcrtcut with the plugin
        """
        assigned_shortcut = self.GetPluginShortcuts(pluginId)
        given_shortcut = self.KeySequencetoStrokeData(keySequence)
        if len(assigned_shortcut) == 1 and assigned_shortcut[0] == given_shortcut: # 唯一
            return True
        if len(assigned_shortcut) > 1 and given_shortcut in assigned_shortcut: # 其中之一
            return True
        if not assigned_shortcut: # 没用指认快捷键
            return False
        else:
            return False
    # 8.为插件添加快捷键(监测快捷键指认)
    def SetPluginsShortcut(self,keySequence: list[typing.Union[int, str]], pluginId:int):
        #sc_renderflow = [0, '`']
        # tip 如果插件没有指认自定义快捷键
        if self.GetPluginShortcuts(pluginId) is None :
            # tip 如果全局快捷键中没有指定快捷键
            if self.FindShortcutAssign(keySequence) == False :
                try:
                    self.AddShortCut(keySequence,pluginId)
                except:
                    raise RuntimeError("Shortcut assign Failed")
    # 9.打印index信息
    def PrintShortcutInfo(self, shortIndex:int):
        for i in shortIndex:
            bc: c4d.BaseContainer = c4d.gui.GetShortcut(i)        
            print("Index : ", i)
            print("Shortcut : ",c4d.gui.Shortcut2String(bc[0], bc[1]))
            print("PluginID : ",bc[1000])
            print("ManagerId : ",bc[1001])
            print("----------")

# exe 简化修饰键
def GetKeyMod() -> str :
    """
    Get the key str combine with the modifiers

    Returns:
        str: string with modifier key plus by + . (no space)
        1: 'Alt+Ctrl+Shift'
        2: 'Ctrl+Shift'
        3: 'Alt+Shift'
        4: 'Alt+Ctrl'
        5: 'Shift'
        6: 'Ctrl'
        7: 'Alt'
        8: 'None'
    """
    bc = c4d.BaseContainer()
    keyMod = "None" 
    if c4d.gui.GetInputState(c4d.BFM_INPUT_KEYBOARD,c4d.BFM_INPUT_CHANNEL,bc):
        if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QSHIFT:
            if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QCTRL: # Ctrl + Shift
                if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QALT: # Alt + Ctrl + Shift
                    keyMod = 'Alt+Ctrl+Shift'
                else: # Shift + Ctrl
                    keyMod = 'Ctrl+Shift'
            elif bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QALT: # Alt + Shift
                keyMod = 'Alt+Shift'
            else: # Shift
                keyMod = 'Shift'
        elif bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QCTRL:
            if bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QALT: # Alt + Ctrl
                keyMod = 'Alt+Ctrl'
            else: # Ctrl
                keyMod = 'Ctrl'
        elif bc[c4d.BFM_INPUT_QUALIFIER] & c4d.QALT: # Alt
            keyMod = 'Alt'
        else: # No modifier
            keyMod = 'None'
        return keyMod

# # Examples
# # Shortcut Assgn when Start C4D

# 如果插件没有指认自定义快捷键，并且全局快捷键中没有指定快捷键，则为插件指认快捷键

# Import custom library to use in plugin
# import os,sys

# PluginID = 1234567 # Unique ID from www.plugincafe.com

# PLUGIN_PATH, f = os.path.split(__file__)
# Lib_Path = os.path.join(PLUGIN_PATH,"res","lib")
# sys.path.insert(0, Lib_Path)

# try:
#     import shortcut 
#     reload(shortcut)  
#     # help(shortcut)  
# finally:
#     # Remove the path we've just inserted.
#     sys.path.pop(0)

# PLUGINS Codes

# # $ Shortcut Register
# # Check shortcut add add ~ to this Plunin    
# def PluginMessage(id, data):
#     # Shortcut Assign when Start C4D
#     if id == c4d.C4DPL_PROGRAM_STARTED:
#         # tip : list[typing.Union[int, str]]
#         keySequence = [0, '`']  # ~ 
#         shortcut.ShortCut().SetPluginsShortcut(keySequence, PluginID)
#         c4d.EventAdd()
#     return False