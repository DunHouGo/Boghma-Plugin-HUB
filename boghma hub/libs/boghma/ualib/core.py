"""
TODO: UserArea Drag 


| **Node 对象继承关系:**
| Node (BaseHierarchy)
|   | Node2D (BaseFrame)
|       | AreaNode
|           | BaseGraphicsItem
|               | BoxContainer
|                   | HBoxContainer
|                   | VBoxContainer
|               | SimpelTextItem
|               | ClipMapTextItem
|               | RectItem
|               | BitmapItem
|               | BaseBezierItem
|                   | RoundRectItem


"""

import copy
import time
import traceback
from typing import Callable, Union, List

import c4d
from c4d import Vector


import ualib.utils as utils
from ualib.utils import (Signal, BaseFrame, BaseHierarchy, SimpleFlag, SingleBezierObject)


class CoreGeUserArea(c4d.gui.GeUserArea):
    
    def __init__(self, root):
        super().__init__()

        self.min_size = Vector(0,0)
        self.win_size = Vector(0,0)
        self._view = [0,0,0,0]  # x1, y1, x2, y2

        self.drag_fps = 0.03  # 秒
        self.drag_start_min_distance = 3
        self.drag_start_min_time = 0.5

        self.timer_step = self.drag_fps*1000  # 30
        self.timer_enable = True
        self.timer_state = False 
        self.timer_type = 0  # 0 mousein   1 always

        self._inside_draw_process = False
        self._layout_changed = False
        self._redraw = False
        self.root = root

        self.bubble_enable = False
        self.bubble_help = { "title": "Title", "text": "bubble_help"}
    
        self.cursor = None

    def Init(self):
        return True

    def GetMinSize(self):
        return int(self.min_size.x), int(self.min_size.y)

    def Sized(self, w, h):
        if w != self.win_size.x or h != self.win_size.y :
            self.win_size = Vector(w,h)
            self.root.viewport_size_changed.emit([w,h])

    def InitValues(self):
        return True

    def DrawMsg(self, x1, y1, x2, y2, msg):
        self._inside_draw_process = True
        self.OffScreenOn() # Double buffering
        #? view 在有 scroll group 的时候返回的数值会不稳定，
        #? 推荐使用 aua 对象的 get_scroll_area_value 方法
        self._view = [x1, y1, x2, y2]  
        self.root._draw_event(self, parent_region=[x1, y1, x2, y2])
        if self.root.draw_debug_frames:
            for child in self.root.iter_all_children():
                if hasattr(child, "_debug_draw_frame"):
                    child._debug_draw_frame(self)
        self.DrawSetOpacity(1)
        self.set_clipping_region_with(x1,y1,x2,y2)
        self._inside_draw_process = False

    def InputEvent(self, msg):
        return self.new_event(BaseEvent.EVENT_TYPE_DOWN, msg)
            
    def Message(self, msg, result):
        if msg.GetId() == c4d.BFM_GETCURSORINFO:
            if not self.timer_enable:
                return True

            if not self.timer_state:
                self.timer_state = True
                self.SetTimer(int(self.timer_step))  
                return True
            
        if msg.GetId() == c4d.BFM_SCROLLGROUP_OFFSETCHANGED :
            self.root.scrollgroup_offsetchanged.emit()

        
        if self.bubble_enable:
            result.SetId(c4d.BFM_GETCURSORINFO)
            #result.SetInt32(c4d.RESULT_CURSOR, c4d.MOUSE_POINT_HAND)
            result.SetString(c4d.RESULT_BUBBLEHELP_TITLE, self.bubble_help["title"])
            result.SetString(c4d.RESULT_BUBBLEHELP, self.bubble_help["text"])   
            #return True
        if self.cursor:
            result.SetId(c4d.BFM_GETCURSORINFO)
            result.SetInt32(c4d.RESULT_CURSOR, self.cursor)
        
        self._redraw_msg()
        
        return c4d.gui.GeUserArea.Message(self, msg, result)
    


    def Timer(self, msg):  
        if not self.timer_enable or not self.timer_state:
            self.SetTimer(0) 
            return 
        
        x, y = self._get_mouse_local_pos(msg)
        x1, y1, x2, y2 = self._view

        if self.timer_type == 1:  # always
            pass
        else:  # when mouse inside
            if (x < x1 or y < y1 or x >= x2 or y >= y2):
                self.timer_state = False

       
        self.new_event(BaseEvent.EVENT_TYPE_TIMER, msg, data=self.timer_state)

    def _get_mouse_local_pos(self, msg):
        msg = c4d.BaseContainer(msg)
        if (msg[c4d.BFM_INPUT_DEVICE] != c4d.BFM_INPUT_KEYBOARD) or not msg[c4d.BFM_INPUT_ASC]:
            self.GetInputState(c4d.BFM_INPUT_MOUSE, msg.GetInt32(c4d.BFM_INPUT_CHANNEL), msg)
            x, y = msg.GetInt32(c4d.BFM_INPUT_X), msg.GetInt32(c4d.BFM_INPUT_Y)
            self._msg = msg
        else:
            # 这里是为了返回多个输入字符， 连续调用 GetInputState 会打断输入
            msg = self._msg
            x, y = msg.GetInt32(c4d.BFM_INPUT_X), msg.GetInt32(c4d.BFM_INPUT_Y)
           
        map_ = self.Global2Local()
        x += map_['x']
        y += map_['y']
        return x, y
    
    def set_clipping_region_with(self, x1, y1, x2, y2):
        self.SetClippingRegion(x1, y1, x2-x1+1, y2-y1+1)

    def _redraw_msg(self):
        if self._layout_changed:
            self._redraw = False
            self._layout_changed = False
            self.LayoutChanged()
        if self._redraw:
            self._redraw = False
            self.Redraw(True)

    def _set_redraw(self):
        if self._inside_draw_process:
            self._redraw = True
        else:
            self.Redraw(True)

    def _set_layout_changed(self):
        if self._inside_draw_process:
            self._layout_changed = True
        else:
            self.LayoutChanged()

    def new_event(self, event_type, msg, data=None):
        ### Creat Event
        event = BaseEvent(self)
        event._set_event_type(event_type)
        event.init_event_data(msg)  
        if data:
            event["timer_state"] = data

        ### Event Cycle
        self.root._event(event)
        if event.is_cancel():
            return False
        ### Draw
        if event.is_redraw():
            self.Redraw(False)  
        return True
    
    def _iter_drag(self, msg): 
        """
        拖拽返回判定条件： 拖拽距离超过最小拖拽距离， 拖拽时间超过最小拖拽时间

        :param msg: 包含c4d输入事件的c4d.BaseContainer
        :type msg: c4d.BaseContainer
        :yield: 迭代器msg
        :rtype: iterator
        """
        x, y = self._get_mouse_local_pos(msg)
        device = msg.GetInt32(c4d.BFM_INPUT_DEVICE)
        channel = msg.GetInt32(c4d.BFM_INPUT_CHANNEL)
        drag_hold_dt = time.time()
        drag_x, drag_y = x, y
        drag_start = False
        while self.GetInputState(device, channel, msg):
            if not msg.GetInt32(c4d.BFM_INPUT_VALUE): 
                break
            drag_x, drag_y = self._get_mouse_local_pos(msg)
            if (drag_start 
                    or abs(drag_x-x) > self.drag_start_min_distance 
                    or abs(drag_y-y) > self.drag_start_min_distance
                    or (time.time()-drag_hold_dt)>self.drag_start_min_time): 
                yield msg
                drag_start = True
                time.sleep(self.drag_fps)

    def set_mouse_cursor(self, cursor=None):
        """
        | 这样用 set_mouse_cursor("MOUSE_HIDE")
        | MOUSE_HIDE  #Hide cursor.
        | MOUSE_SHOW  #Show cursor.
        | MOUSE_NORMAL  #Normal cursor.
        | MOUSE_BUSY  #Busy cursor.
        | MOUSE_CROSS  #Cross cursor.
        | MOUSE_QUESTION  #Question cursor
        | MOUSE_ZOOM_IN  #Zoom in cursor.
        | MOUSE_ZOOM_OUT  #Zoom out cursor.
        | MOUSE_FORBIDDEN  #Forbidden cursor.
        | MOUSE_DELETE  #Delete cursor.
        | MOUSE_COPY  #Copy cursor.
        | MOUSE_INSERTCOPY  #Insert copy cursor.
        | MOUSE_INSERTCOPYDOWN  #Insert copy down cursor.
        | MOUSE_MOVE  #Move cursor.
        | MOUSE_INSERTMOVE  #Insert move cursor.
        | MOUSE_INSERTMOVEDOWN  #Insert move cursor.
        | MOUSE_ARROW_H  #Horizontal cursor.
        | MOUSE_ARROW_V  #Vertical cursor.
        | MOUSE_ARROW_HV  #Horizontal and vertical arrow cursor.
        | MOUSE_POINT_HAND  #Point hand cursor.
        | MOUSE_MOVE_HAND  #Move hand cursor.
        | MOUSE_IBEAM  #I-beam cursor.
        | MOUSE_SELECT_LIVE  #Live selection cursor.
        | MOUSE_SELECT_FREE  #Free selection cursor.
        | MOUSE_SELECT_RECT  #Rectangle selection cursor.
        | MOUSE_SELECT_POLY  #Polygon selection cursor.
        | MOUSE_SPLINETOOLS  #Spline tools cursor.
        | MOUSE_EXTRUDE  #Extrude cursor.
        | MOUSE_NORMALMOVE  #Normal move cursor.
        | MOUSE_ADDPOINTS  #Add points cursor.
        | MOUSE_ADDPOLYGONS  #Add polygons cursor.
        | MOUSE_BRIDGE  #Bridge cursor.
        | MOUSE_MIRROR  #Mirror cursor.
        | MOUSE_PAINTMOVE  #Paint move cursor.
        | MOUSE_PAINTSELECTRECT  #Paint select rectangle cursor.
        | MOUSE_PAINTSELECTCIRCLE  #Paint select circle cursor.
        | MOUSE_PAINTSELECTPOLY  #Paint select polygon cursor.
        | MOUSE_PAINTSELECTFREE  #Paint select free cursor.
        | MOUSE_PAINTMAGICWAND  #Paint magic wand cursor.
        | MOUSE_PAINTCOLORRANGE  #Paint color range cursor.
        | MOUSE_PAINTFILL  #Paint fill cursor.
        | MOUSE_PAINTPICK  #Paint pick cursor.
        | MOUSE_PAINTBRUSH  #Paint brush cursor.
        | MOUSE_PAINTCLONE  #Paint clone cursor.
        | MOUSE_PAINTTEXT  #Paint text cursor.
        | MOUSE_PAINTCROP  #Paint crop cursor.
        | MOUSE_PAINTLINE  #Paint line cursor.
        | MOUSE_PAINTPOLYSHAPE  #Paint polygon shape cursor
        """
        if cursor is None:
            self.cursor = None
        else:
            self.cursor = eval(f"c4d.{cursor}")



class BaseEvent: 

    """
    基础事件对象，会在每一个事件循环周期由 GeUserArea.InputEvent() 和 GeUserArea.Timer() 创建，并通过 GeUserArea.root._event() 方法传递到节点子级

    .. note::
        | 一个事件循环周期是指： 
        |    输入事件发生 -> 事件传遍整个节点树 -> 数据刷新 -> 节点绘制


    | BaseEvent对象主要有以下几种事件：

    .. hlist::
        :columns: 1

        * is_down_event() -> EVENT_TYPE_DOWN 按下事件 由InputEvent发起
        * is_hold_event() -> EVENT_TYPE_HOLD 拖拽事件 由is_down_event发起
        * is_up_event() -> EVENT_TYPE_UP   松开事件 由is_down_event发起
        * is_timer_event() -> EVENT_TYPE_TIMER 计时器事件 由Timer发起


    | 可获取的事件数据包括 ：

    .. hlist::
        :columns: 1

        * **mouse_event_position** :列表[x,y] 对应事件按键点击时鼠标的位置
        * **mouse_down_position** : 列表[x,y] 按键点击时鼠标的位置
        * **mouse_hold_position** : 列表[x,y] 按键点击并拖动时鼠标的位置
        * **mouse_up_position** : 列表[x,y] 按键松开时鼠标的位置
        * **qualifier** : 辅助键位事件 如: ctrl/shift等, 对应 self.QUALIFIERS_CTRL/self.QUALIFIERS_SHIFT ...
        * **device** :  输入设备: 鼠标 self.DEVICE_MOUSE, 键盘 self.DEVICE_KEYBOARD
        * **channel** : 输入按键: 鼠标左键中间右键 self.CHANNEL_MOUSELEFT/ self.CHANNEL_MOUSERIGHT/ self.CHANNEL_MOUSEMIDDLE 等等
        * **value** : 输入按键对应数据, 比如滚轮事件的数据
        * **doubleclick** : 是否是双击

    .. note::
        | 基础的事件数据（_event_data）可以通过 __getitem__ 方法获取

        .. code-block:: python

            def _event(self, event: BaseEvent):
                x, y = event["mouse_down_position"]
                ...

    | 在一个事件周期内希望重新绘制时，需要调用 **event.set_redraw()** 方法
    | 该方法不会立即绘制而是等待所有输入事件结束后调用 root._draw_event()
    | 需要取消事件时，调用 event.set_cancel() 方法, 这样c4d 其他界面控件就可以捕获到这个事件并作出反馈。
        
    """
    # event_data中对应的基础事件ID, 所有事件ID都跟随C4D中的ID号
    QUALIFIERS_NONE = 0
    QUALIFIERS_SHIFT = 1
    QUALIFIERS_CTRL = 2
    QUALIFIERS_ALT = 4

    DEVICE_MOUSE = 1836021107
    DEVICE_KEYBOARD = 1801812322

    CHANNEL_MOUSELEFT = 1
    CHANNEL_MOUSERIGHT = 2
    CHANNEL_MOUSEMIDDLE = 3
    CHANNEL_MOUSEWHEEL = 100
    CHANNEL_MOUSEMOVE = 101
    
    EVENT_TYPE_NONE = 0
    EVENT_TYPE_DOWN = 1
    EVENT_TYPE_HOLD = 2
    EVENT_TYPE_UP = 3
    EVENT_TYPE_TIMER = 4

    def __init__(self, CORE):
        self._CORE = CORE
        self._msg = None
        self._event_data = {}
        self._event_type = self.EVENT_TYPE_NONE
        self.init()

    def __getitem__(self, key):
        return self._event_data[key]
    
    def __setitem__(self, key, value):
        self._event_data[key] = value

    def init(self):
        self._handled = False
        self._handled_message = None
        self._cancel = False
        self._redraw = False

    def init_event_data(self, msg):
        self._msg = msg
        x, y = self._CORE._get_mouse_local_pos(msg)
        device = msg.GetInt32(c4d.BFM_INPUT_DEVICE)
        channel = msg.GetInt32(c4d.BFM_INPUT_CHANNEL)
        qualifier = msg.GetInt32(c4d.BFM_INPUT_QUALIFIER)
        value = msg.GetInt32(c4d.BFM_INPUT_VALUE)
        doubleclick = msg.GetInt32(c4d.BFM_INPUT_DOUBLECLICK)
        asc = msg[c4d.BFM_INPUT_ASC]
       
        self["mouse_event_position"] = [x, y]
        self["mouse_down_position"] = [x, y]
        self["mouse_hold_position"] = [x, y]
        self["mouse_up_position"] = [x, y]
        self["qualifier"] = qualifier
        self["device"] = device
        self["channel"] = channel
        self["value"] = value
        self["doubleclick"] = doubleclick
        self["asc"] = asc
        self["timer_state"] = False

    def clone(self):
        event = BaseEvent(self._CORE) 
        event._event_data = copy.deepcopy(self._event_data)
        event._event_type = self._event_type
        event._msg = self._msg.GetClone(c4d.COPYFLAGS_NONE)
        event.init()
        return event

    def set_handled(self, handled_message=None):
        """
        设置事件为已处理，这里的处理只是个布尔值，实际上并不会发生任何事情
        需要用户自己通过 is_handled() 来判定事件是否在传入前已经被其他对象处理过

        .. note::
            已处理的事件在AreaNode中将不再向下传递

        如果你想要覆写 _event 方法，可以如下使用：

        .. code-block:: python

            def _event(self, event):
                super()._event(event)
                if not event.is_handled:
                    # 执行你想要执行的功能
                    pass

        :param handled_message: 可以向上层对象返回处理事件的对象, 默认为 None
        :type handled_message: any
        """
        self._handled = True
        self._handled_message = handled_message

    def is_handled(self):
        """
        事件是否已处理

        :rtype: bool
        :return: 返回True 如果事件已处理
        """
        return self._handled
    
    def set_cancel(self):
        """
        设置事件为取消，事件会继续向下传递但不会有任何效果
        此方法可以用于取消特定事件占用 c4d 界面其他控件的事件输入，
        
        .. note::

            设置时, 在 GeUserArea.InputEvent() 中返回 False
            比如：滚轮事件如果不使用 set_cancel() 来取消， 则用户就无法通过滚轮来让 ScrollGroup 滚动
            
        """
        self._cancel = True

    def is_cancel(self):
        """
        事件是否取消

        :rtype: bool
        :return: 返回True 如果事件已取消
        """
        return self._cancel

    def set_redraw(self):
        """
        延迟调用绘制，在一个事件循环周期结束后调用 GeUserArea.Redraw() 方法
        """
        self._redraw = True

    def is_redraw(self):
        """
        绘制是否被调用

        :rtype: bool
        :return: 返回True 如果需要绘制
        """
        return self._redraw
    
    def _set_event_type(self, event_type):
        """
        :type event_type: int
        :param event_type: 事件类型 
        """
        self._event_type = event_type
    # event type
    def is_down_event(self):
        """
        按下事件 

        :rtype: bool
        :return: 除了鼠标悬停外的所有事件都会返回True
        """
        return self._event_type == self.EVENT_TYPE_DOWN
    def is_hold_event(self):
        """
        拖拽事件

        :rtype: bool
        :return: 当发生拖拽时，除了鼠标悬停外的所有事件都会返回True
        """
        return self._event_type == self.EVENT_TYPE_HOLD
    def is_up_event(self):
        """
        松开事件

        :rtype: bool
        :return: 除了鼠标悬停外的所有事件都会返回True
        """
        return self._event_type == self.EVENT_TYPE_UP
    def is_timer_event(self):
        """
        计时器事件

        :rtype: bool
        :return: 主要是鼠标悬停事件时返回True
        """
        return self._event_type == self.EVENT_TYPE_TIMER

    # Mouse Input
    def is_mouse_pressed(self):
        """
        输入事件为鼠标事件

        :rtype: bool
        :return: 鼠标事件返回True
        """
        return self["device"] == self.DEVICE_MOUSE
    
    def get_mouse_pos(self):
        """
        获取当前事件中的鼠标位置，down hold up timer都可以返回

        .. note::
            除了通过这个方法，也可以通过 event[key]的方式(如event["mouse_down_position"])在不同事件中获取其他事件的鼠标位置。
                
            .. hlist::
                :columns: 1

                * mouse_event_position :列表[x,y] 对应事件按键点击时鼠标的位置。
                * mouse_down_position : 列表[x,y] 按键点击时鼠标的位置。
                * mouse_hold_position : 列表[x,y] 按键点击并拖动时鼠标的位置。
                * mouse_up_position : 列表[x,y] 按键松开时鼠标的位置。

        .. code-block:: python

            def _event(self, event: BaseEvent):
                # 等于 x, y = event["mouse_event_position"]
                x, y = event.get_mouse_pos()
                ...

        .. seealso::
            :doc:`__getitem__` 中有所有可获取的 **event** 数据        
        
        :rtype: list
        :return: [x,y] 鼠标相对画布的位置
        """
        return self["mouse_event_position"]
    def is_double_click(self):
        """
        是否是双击

        :rtype: bool
        :return: 双击时返回True
        """
        return self["doubleclick"]
    def is_mouse_left_pressed(self):
        """
        鼠标左键点击

        :rtype: bool
        :return: 左键点击时为True
        """
        return self["channel"] == self.CHANNEL_MOUSELEFT
    def is_mouse_right_pressed(self):
        """
        鼠标右键点击

        :rtype: bool
        :return: 右键点击时返回True
        """
        return self["channel"] == self.CHANNEL_MOUSERIGHT
    def is_mouse_middle_pressed(self):
        """
        滚轮点击（又称为中键）

        :rtype: bool
        :return: 中键点击时返回True
        """
        return self["channel"] == self.CHANNEL_MOUSEMIDDLE
    def is_mouse_wheel_scrolled(self):
        """
        滚轮滚动

        :rtype: bool
        :return: 滚轮滚动时返回True
        """
        return self["channel"] == self.CHANNEL_MOUSEWHEEL
    def get_wheel_value(self):
        """
        获取滚轮每次滚动的数值

        :rtype: bool
            int: 每次滚轮滚动的量
        """
        return self["value"]

    # Keyboard Input
    def is_key_pressed(self):
        """
        是否是键盘输入事件

        :rtype: bool
        :return: 当键盘输入时返回True
        """
        return self["device"] == self.DEVICE_KEYBOARD
    def get_key_value(self):
        return self["asc"]
    def is_special_key_pressed(self, key=c4d.KEY_F1):
        """
        KEY_MLEFT
        KEY_MRIGHT
        KEY_MMIDDLE
        KEY_MX1
        KEY_MX2
        KEY_SHIFT
        KEY_CONTROL
        KEY_ALT
        KEY_CAPSLOCK
        KEY_MODIFIERS
        KEY_COMMAND
        KEY_BACKSPACE
        KEY_TAB
        KEY_ENTER
        KEY_ESC
        KEY_SPACE
        KEY_DELETE
        KEY_UP
        KEY_DOWN
        KEY_LEFT
        KEY_RIGHT
        KEY_PGUP
        KEY_PGDOWN
        KEY_HOME
        KEY_END
        KEY_INSERT
        KEY_F1
        KEY_F2
        KEY_F3
        KEY_F4
        KEY_F5
        KEY_F6
        KEY_F7
        KEY_F8
        KEY_F9
        KEY_F10
        KEY_F11
        KEY_F12
        KEY_F13
        KEY_F14
        KEY_F15
        KEY_F16
        KEY_F17
        KEY_F18
        KEY_F19
        KEY_F20
        KEY_F21
        KEY_F22
        KEY_F23
        KEY_F24
        KEY_F25
        KEY_F26
        KEY_F27
        KEY_F28
        KEY_F29
        KEY_F30
        KEY_F31
        KEY_F32
        """
        return self["channel"] == key
    def is_shift_pressed(self):
        """
        shift点击

        :rtype: bool
        :return: shift点击时返回True
        """
        return self["qualifier"] == self.QUALIFIERS_SHIFT
    def is_ctrl_pressed(self):
        """
        ctrl点击

        :rtype: bool
        :return: ctrl点击时返回True
        """
        return self["qualifier"] == self.QUALIFIERS_CTRL
    def is_alt_pressed(self):
        """
        alt点击

        :rtype: bool
        :return: alt点击时返回True
        """
        return self["qualifier"] == self.QUALIFIERS_ALT

######################### BASE NODES

class Node(BaseHierarchy):
    """ 
    最基础的抽象对象
    继承自 BaseHierarchy类 所以可以实现不同Node对象间的父子级关系

    :param prop: 用于管理Node对象所有的常规属性 (后续prop属性会用 <prop> 表示)
    :type prop: dict
    :param dirty_flag: 用于内部刷新使用的标志位对象
    :type dirty_flag: SimpleFlag
    :param user_flag: 用户可以自由使用的标志位对象
    :type user_flag: SimpleFlag

    """
    DIRTYFLAGS_MATRIX = "matrix"
    DIRTYFLAGS_CHANGES= "changes"

    def __init__(self):
        super().__init__() 
        self.prop_changed = Signal()
        self.prop = {}
        self.prop["enable"] = True
        self.prop["visiable"] = True
        self.dirty_flag = SimpleFlag([self.DIRTYFLAGS_MATRIX, self.DIRTYFLAGS_CHANGES])
        self.user_flag = SimpleFlag()

    def change_prop(self, key, value):
        if key in self.prop:
            self.prop[key] = value
            self.prop_changed.emit(key, value)
        else:
            raise ValueError(f"prop key not exists.  key:{key}")


    def _event(self, event: BaseEvent):
        """  
        事件处理,会将事件自动向下传递

        :meta public:
        
        采用事件冒泡的规则，优先处理子对象的事件再处理父对象，当 event.is_handled() 为True 事件停止转递，
        覆写方法时应该先调用 super()._event(event) 再根据 event.is_handled() 的状态执行相应代码。

        :param event: 基础事件对象
        :type event: BaseEvent

        """


        if event.is_handled() or not self.prop["visiable"] or not self.prop["enable"]:
            return 
        
        for object in self.get_children():
            if not object.prop["visiable"] or not object.prop["enable"]:
                continue 
            object._event(event)
            if event.is_handled():
                break
        
        

    def _draw_event(self, ua, parent_region: list):
        """
        绘制事件

        :meta public:

        .. note:: 
            如果覆写该方法需要注意：内部刷新事件需要在绘制前调用并尽量遵循以下原则：
            
            .. hlist::
                :columns: 1

                * 1.先调用 _update() 进行数据刷新
                * 2.调用 _draw() 绘制当前对象
                * 3.调用 _draw_child() 绘制子对象
                * 4.调用 dirty_flag.clear_all_flags() 清理本次事件循环产生的 dirty flag
                * 5.调用 user_flag.clear_all_flags() 清理本次事件循环产生的 user flag

        :param ua: core 模块中的 CoreGeUserArea 对象
        :type ua: CoreGeUserArea
        :param parent_region: [x1,y1,x2,y2]
        :type parent_region: list

        """
        self._update() 
        self._draw(ua)
        self._draw_child(ua, parent_region)
        self.dirty_flag.clear_all_flags()  # call after all draw finished
        self.user_flag.clear_all_flags()  # call after all draw finished
    
    def _update(self):
        """
        刷新绘制数据
        
        :meta public:

        .. note:: 
            _update 方法会在 _draw_event 中自动调用，当执行具体的数据刷新时可以利用 dirty flag 来判断刷新时机避免无效的反复刷新（可以极大的提升效率）

            .. code-block:: python

                def _update(self):
                    if self.dirty_flag.has_flag(self.DIRTYFLAGS_CHANGES):
                        # 内部数据更新代码写这里
                    elif self.dirty_flag.has_flag(self.DIRTYFLAGS_MATRIX):
                        # 位置变换数据更新代码写这里
            
        .. warning::
            _update() 本质上是在DrawMsg() 函数中调用的, 所以注意避免直接调用 CoreGeUserArea 的 LayoutChanged() 方法 , 否则可能会因陷入死循环而导致的C4D崩溃


        """
        pass
    
    def _draw(self, ua):
        """ 
        绘制覆写方法，在这里一般只需绘制当前对象本身

        :meta public:

        :param ua: core 模块中的 CoreGeUserArea 对象
        :type ua: CoreGeUserArea
        """

    def _draw_child(self, ua, parent_region:list):
        """ 
        子对象绘制覆写方法，在这里一般绘制所有子对象，从后向前绘制，列表首位的子对象会显示在视图最上层
        
        :meta public:

        .. note:: 
            insert_under方法会将子对象添加到 _children 列表的首位
            insert_underlast 会添加到末尾
            注意两种不同方式添加子对象绘制出来的前后顺序会不一样
            其他添加方法查看 BaseHierarchy

        :param ua: core 模块中的 CoreGeUserArea 对象
        :type ua: CoreGeUserArea
        """
        for object in reversed(self.get_children()):
            if not object.prop["visiable"]:
                continue 
            object._draw_event(ua, parent_region)


class Node2D(Node, BaseFrame):
    """
    最基础的2D对象, 所有对象应该基于这个类创建

    除了继承 Node类, 最重要的是Node2D继承了 BaseFrame类， 可以设置位置大小等参数
    也可以通过 get_global_position() 在嵌套的父子级关系中获取全局坐标，方便用来最终绘制 

    常用的输入事件覆写以下方法使用：

    .. hlist::
        :columns: 1

        * **_mouse_move_event** 鼠标悬停
        * **_doubleclick_event** 双击
        * **_mouse_press_event** 鼠标点击
        * **_key_press_event** 键盘点击
        * **_wheel_event** 鼠标滚轮
        * **_mouse_drag_start_event** 鼠标拖拽开始
        * **_mouse_drag_process_event** 鼠标拖拽
        * **_mouse_drag_release_event** 鼠标拖拽结束


    :param global_frame_changed: 当对象的位置发送改变时发射信号，并将所有下级的 DIRTYFLAGS_MATRIX 设置为 True
    :type global_frame_changed: Signal

    """

    def __init__(self):
        super().__init__() 
        # global_frame_changed 是 BaseFrame 的 Signal
        self.global_frame_changed.connect(self._on_global_frame_changed)
   
    def _on_global_frame_changed(self):
        """ 
        :meta public:

        当对象的全局位置发生改变时自动调用该方法，将自己以及所有的子对象（包括曾子孙）的 dirty_flag 设立 DIRTYFLAGS_MATRIX 标志位
        用于在后续的刷新中使用
        """
        self.dirty_flag.set_flag(self.DIRTYFLAGS_MATRIX)
        for child in self.iter_all_children():
            child.dirty_flag.set_flag(self.DIRTYFLAGS_MATRIX)

    def _debug_draw_frame(self, ua):
        """
        :meta public:
        此方法用于 debug, 用户只需将 AUA.ua.draw_debug_frames 设为True 则所有 Node2D 都会绘制用于debug的红色虚线外轮廓
        """
        ua.DrawSetOpacity(1)
        ua.DrawSetPen(Vector(1,0,0))
        ua.DrawFrame(*self.get_global_bbox(), lineWidth=1, lineStyle=c4d.LINESTYLE_DASHED)

    def _event(self, event: BaseEvent):
        """
        基础事件分发执行
        """
        super()._event(event)
        
        if event.is_handled():
            return 
        if event.is_timer_event():
            self._mouse_move_event(event)
        elif event.is_mouse_pressed():
            if event.is_mouse_wheel_scrolled():
                self._wheel_event(event)
            elif event.is_down_event():
                self._mouse_press_event(event)
                if event.is_double_click():
                    self._doubleclick_event(event)
                    
        elif event.is_key_pressed():
            if event.is_down_event():
                self._key_press_event(event)

    def _mouse_move_event(self, event: BaseEvent):
        """覆写方法

        :meta public:

        鼠标悬停移动事件
        可以通过 event.get_mouse_pos() 方法获取当前事件中的鼠标位置

        :param event: 基础事件
        :type event: BaseEvent
        """

    def _doubleclick_event(self, event: BaseEvent):
        """覆写方法

        :meta public:

        鼠标双击事件
        可以通过 event.is_mouse_left_pressed() 方法获取是否是左键双击

        :param event: 基础事件
        :type event: BaseEvent
        """
         
    def _mouse_press_event(self, event: BaseEvent):
        """覆写方法

        :meta public:

        鼠标点击事件
        可以通过 event.get_mouse_pos() 方法获取当前事件中的鼠标位置
        可以通过 event.is_mouse_left_pressed() 方法获取是否是左击
        可以通过 event.is_mouse_right_pressed() 方法获取是否是右击

        :param event: 基础事件
        :type event: BaseEvent
        """
 

    def _key_press_event(self, event: BaseEvent):
        """覆写方法

        :meta public:

        键盘点击事件
        可以通过 event.get_key_value() 方法获取当前输入的字符

        :param event: 基础事件
        :type event: BaseEvent
        """


    def _wheel_event(self, event: BaseEvent):
        """覆写方法

        :meta public:

        鼠标滚轮事件
        可以通过 event.get_wheel_value() 方法获取当前输入的滚动量

        .. note::
            注意：此事件默认调用 event.set_cancel() （可以防止拦截 ScrollGroup 的滚轮事件）

        :param event: 基础事件
        :type event: BaseEvent
        """
        event.set_cancel()
     
    def start_drag_event(self, event: BaseEvent):
        """
        开始拖拽事件。在 _mouse_press_event 中调用该方法可以激活 _mouse_drag_start_event，_mouse_drag_process_event，_mouse_drag_release_event 事件

        .. code-block:: python

            def _mouse_press_event(event):
                print("press called")

                # 可以先在上方执行鼠标按压命令，再调用拖拽。
                self.start_drag_event(event)

            def _mouse_drag_start_event(self, event: BaseEvent):
                print("drag_start called")

            def _mouse_drag_process_event(self, event: BaseEvent):
                print("drag_process called")

            def _mouse_drag_release_event(self, event: BaseEvent):
                print("drag_release called")

            # >>> "press called"
            # >>> "drag_start called"
            # >>> "drag_process called"
            # >>> "drag_release called"

        :param event: 基础事件
        :type event: BaseEvent
        :raises TypeError: 此事件必须要在 _mouse_press_event 函数中调用
        """
        if event.is_handled():
            return 
        if not event.is_mouse_pressed() or not event.is_down_event():
            raise TypeError("start_drag_event ERROR: can only call start_drag_event from _mouse_press_event")
        
        # drag
        x, y = event["mouse_down_position"]
        hold_start = 1
        clone_event = event.clone()
        for msg in clone_event._CORE._iter_drag(clone_event._msg):
            clone_event.init_event_data(msg)
            clone_event["mouse_down_position"] = [x, y]
            clone_event.init()
            clone_event._set_event_type(clone_event.EVENT_TYPE_HOLD)
            if hold_start == 1:
                hold_start = 0
                self._mouse_drag_start_event(clone_event)
            else:
                self._mouse_drag_process_event(clone_event)
                
            if clone_event.is_redraw():
                event.set_redraw()
                event._CORE.Redraw()
            if clone_event.is_cancel():
                event.set_handled()
                event.set_cancel()
                break
            elif clone_event.is_handled():
                event.set_handled()
                break

        # release
        if not event.is_handled():
            clone_event = clone_event.clone()
            clone_event.init()
            clone_event._set_event_type(clone_event.EVENT_TYPE_UP)
            self._mouse_drag_release_event(clone_event)
            if clone_event.is_redraw():
                event.set_redraw()
            if clone_event.is_cancel():
                event.set_handled()
                event.set_cancel()
            elif clone_event.is_handled():
                event.set_handled()
    
    def _mouse_drag_start_event(self, event: BaseEvent):
        """覆写方法

        :meta public:

        鼠标拖拽事件，通过 start_drag_event() 激活。
        
        .. note::
            只会在拖拽开始时调用一次。
        
        :param event: 基础事件
        :type event: BaseEvent
        """
    
    def _mouse_drag_process_event(self, event: BaseEvent):
        """覆写方法

        :meta public:

        鼠标拖拽事件，通过 start_drag_event() 激活。
                
        :param event: 基础事件
        :type event: BaseEvent
        """

    def _mouse_drag_release_event(self, event: BaseEvent):
        """覆写方法

        :meta public:

        鼠标拖拽事件，通过 start_drag_event() 激活。

        .. note::
            只会在拖拽结束时调用一次。
                
        :param event: 基础事件
        :type event: BaseEvent
        """


class AreaNode(Node2D):
    """ 
    基础区域对象, 事件只有在区域内部发生才会向下传递, 绘制也可以限制在区域内部
    
    :param mouse_entered: 鼠标进入区域时发送信号
    :type mouse_entered: Signal
    :param mouse_leave: 鼠标退出区域时发送信号
    :type mouse_leave: Signal

    :param clip_to_frame: <prop> True 裁剪对象绘制范围到自己的 baseframe 范围内, False 关闭裁剪. 细节可以查看 draw_event
    :type clip_to_frame: bool
    :param clip_children: <prop> True 裁剪子对象绘制范围到当前对象的 baseframe 范围内, False 关闭裁剪. 细节可以查看 draw_event
    :type clip_to_frame: bool
    :param clip_optimize: <prop> 用于高效渲染, 建议设为True, 会将 baseframe 超出视图区域的对象跳过绘制(draw). 细节可以查看 draw_event
    :type clip_to_frame: bool

    其他参数：mouse_inside 鼠标在区域内部时为True
        
    """

    def __init__(self):
        super().__init__()
        
        self.mouse_entered = Signal(AreaNode)
        self.mouse_leave = Signal(AreaNode)

        self.prop["clip_to_frame"] = True   
        self.prop["clip_children"] = True   
        self.prop["clip_optimize"] = True  

        self.mouse_inside = False
        self._was_inside = False
        self._extend_shapes = []

    def _event(self, event: BaseEvent):
        """
        :meta public:

        只有当鼠标在区域内部时向下传递事件

        """
        if event.is_handled():
            return 
        x, y = event.get_mouse_pos()
        is_inside = self._check_inside(x, y)

        if is_inside and not self._was_inside:
            self._was_inside = True
            self.mouse_entered.emit(self)
            self._mouse_enter_event(event)
        elif not is_inside and self._was_inside:
            # 鼠标出界后会额外调用一次
            is_inside = True
            self._was_inside = False
            self.mouse_leave.emit(self)
            self._mouse_leave_event(event)

        self.mouse_inside = is_inside

        if self.mouse_inside:
            super()._event(event)
 
    def _mouse_enter_event(self, event: BaseEvent):
        """
        :meta public:

        鼠标进入事件在这里执行
        """

    def _mouse_leave_event(self, event: BaseEvent):
        """
        :meta public:

        鼠标离开事件在这里执行
        """

    def _check_inside(self, x, y):
        """检查鼠标位置是否在对象内部

        需要注意 影响鼠标是否在对象内部除了当前对象的 BaseFrame.is_point_inside() 方法外，还会考虑到 _extend_shapes
        开发者可以考虑调用 extend_shapes() 方法来扩展鼠标在当前对象内部判定的区域

        
        :rtype: bool
        :return: 在内部返回True
        """
        is_inside = self.is_point_inside(x, y)
        if not is_inside:  # 如果以及为True了就无需再进一步判定
            # 遍历所有的 _extend_shapes 额外判断是否在内部
            for shape in self._extend_shapes:
                is_inside = is_inside or shape.is_point_inside(x, y)
        return is_inside

    def _draw_event(self, ua, parent_region: list):
        """ 区域对象的绘制判定

        这里复杂在于会利用 parent_region 和当前对象的 BaseFrame来跳过无需绘制的对象（会极大的提升效率）
        而且只有当绘制时才会调用刷新。

        """
        overlap = self.get_overlap_rect_with(*parent_region)
        drawed = False
        # draw self
        if self.prop["clip_to_frame"] and overlap:
            ua.set_clipping_region_with(*overlap)
            self._update()
            if self.prop["visiable"]: 
                self._draw(ua)
                drawed = True
        elif overlap or not self.prop["clip_optimize"] :
            ua.set_clipping_region_with(*parent_region)
            self._update()
            if self.prop["visiable"]: 
                self._draw(ua)
                drawed = True

        # draw children
        if self.prop["clip_children"] and overlap:
            self._draw_child(ua, overlap)
        elif overlap or not self.prop["clip_optimize"]:
            self._draw_child(ua, parent_region)
        ua.set_clipping_region_with(*parent_region)
        if drawed:
            self.dirty_flag.clear_all_flags()
            self.user_flag.clear_all_flags() 

    def extend_shapes(self, shapes=[]):
        """ 扩展当前对象内部判定区域， 在 _check_inside 函数中使用

        Args:
            shapes (list, optional): BaseFrame对象组成的列表. Defaults to [].
        """
        for shape in shapes:
            assert hasattr(shape, "is_point_inside"), "shape must be a BaseFrame object"
        self._extend_shapes = shapes

    

class BaseGraphicsItem(AreaNode):
   
    """ 
    基础图形对象, 事件只有在区域内部发生才会向下传递, 绘制也可以限制在区域内部
       
    :param moveable: <prop> True 前对象可以被拖拽
    :type moveable: bool
    :param focus: <prop> 当前对象被聚焦时返回 True
    :type focus: bool
    :param selectable: <prop> True 对象可被选择
    :type selectable: bool
    :param selected: <prop> 当前对象被选择时返回 True
    :type selected: bool
    :param color: <prop> 绘制时使用的默认颜色
    :type color: c4d.Vector
    :param opacity: <prop> 绘制时使用的默认透明度 (0-1)
    :type opacity: float

        
    """

    DEFUALT_COLOR = Vector(0.5,0.4,0.2)

    # align flag
    BFH_CENTER = c4d.BFH_CENTER
    BFH_LEFT = c4d.BFH_LEFT
    BFH_RIGHT = c4d.BFH_RIGHT
    BFH_FIT = c4d.BFH_FIT
    BFH_SCALE = c4d.BFH_SCALE
    BFH_SCALEFIT = c4d.BFH_SCALEFIT

    BFV_CENTER = c4d.BFV_CENTER
    BFV_TOP = c4d.BFV_TOP
    BFV_BOTTOM = c4d.BFV_BOTTOM
    BFV_FIT = c4d.BFV_FIT
    BFV_SCALE = c4d.BFV_SCALE
    BFV_SCALEFIT = c4d.BFV_SCALEFIT

    def __init__(self):
        super().__init__()

        self.prop["moveable"] = False
        self.prop["focus"] = False
        self.prop["selectable"] = True
        self.prop["selected"] = False
        self.prop["color"] = self.DEFUALT_COLOR
        self.prop["opacity"] = 1
        self.prop["minsize"] = Vector()
        self.prop["align_flag"] = 0

        self._start_position = None
        self._drag_mouse_follow = 0.35
    
    def _mouse_press_event(self, event: BaseEvent):
        self.prop["focus"] = True
        if event.is_mouse_left_pressed() and self.prop["moveable"]:
            self.start_drag_event(event)
        
    def _mouse_drag_start_event(self, event: BaseEvent):
        if self.prop["moveable"] : 
            self._start_position = self.position
    
    def _mouse_drag_process_event(self, event: BaseEvent):
        if self.prop["moveable"] : 
            sx, sy = event["mouse_down_position"]
            dx, dy = event["mouse_hold_position"]
            aim = self._start_position+Vector(dx-sx, dy-sy)
            self.position += (aim-self.position)*self._drag_mouse_follow
            event.set_redraw()

    def set_drag_mouse_follow(self, value=0.35):
        """
        拖拽时的对象跟随鼠标延迟，通常保持默认即可。

        :param value: 0 到 1 之间。设置为 1 时完全没有延迟。, defaults to 0.35
        :type value: float, optional
        """
        self._drag_mouse_follow = value

    def _draw_event(self, ua, parent_region: list):
        if isinstance(self.prop["color"], int):
            color = ua.GetColorRGB(self.prop["color"])
            self.prop["color"] = Vector(color["r"], color["g"], color["b"])/255.0
        return super()._draw_event(ua, parent_region)

    def _sized(self, size):
        self.size = size

    def _get_minsize(self):
        return self.prop['minsize']


######################### GraphicsItem Container

class BoxContainer(BaseGraphicsItem):

    LINESTYLE_NORMAL = c4d.LINESTYLE_NORMAL
    LINESTYLE_DOTTED = c4d.LINESTYLE_DOTTED
    LINESTYLE_DASHED = c4d.LINESTYLE_DASHED
    LINESTYLE_DASHED_INV = c4d.LINESTYLE_DASHED_INV
    LINESTYLE_DASHED_BIG = c4d.LINESTYLE_DASHED_BIG

    def __init__(self, position=Vector(), size=Vector(), gap=10, border=[10,10,10,10]):
        super().__init__()
        self.position = position
        self.size = size
        self.prop["gap"] = gap
        self.prop["border"] = border  # 左上右下
    
    def _get_minsize(self):
        pass
    
    def _update(self):
        if self.dirty_flag.has_flag(self.DIRTYFLAGS_CHANGES):
            self._align()

    def add_child(self, item, align_flag=c4d.BFH_CENTER|c4d.BFV_CENTER, minsize=Vector(1)):
        item.insert_underlast(self)
        item.prop["minsize"] = minsize
        item.prop["align_flag"] = align_flag
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

    def _sized(self, size):
        self.size = Vector(size[0], size[1])
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

    def _align(self):
        pass

class HBoxContainer(BoxContainer):

    def __init__(self, position=Vector(), size=Vector(), gap=10, border=[10,10,10,10]):
        super().__init__(position, size, gap, border)
        
    def _get_minsize(self):
        childs = self.get_children()
        gap = self.prop['gap']
        bl, bt, br, bb = self.prop["border"]
        minsize = Vector()
        ymax = 0
        for child in childs:
            child_minsize = child._get_minsize()
            minsize.x += child_minsize.x
            ymax = max(ymax, child_minsize.y)
        minsize.y = ymax + bt + bb
        minsize.x += bl + br + gap*(len(childs)-1)
        self.prop['minsize'] = minsize
        return minsize

    def _align(self):
        minsize = self._get_minsize()
        left_size = self.size - minsize
        childs = self.get_children()
        gap = self.prop['gap']
        bl, bt, br, bb = self.prop["border"]

        # scale
        scale_counter = 0
        aim_size_y = minsize.y -bt -bb 
        for child in childs:
            child.offset = child.ALIGNMENT_LEFT_TOP
            if child.prop["align_flag"] & child.BFH_SCALE:
                scale_counter += 1
            if child.prop["align_flag"] & child.BFV_SCALE:
                aim_size_y = self.size.y -bt -bb 
        each = left_size.x/float(scale_counter) if scale_counter>0 else 0
        
        # 
        x, y = bl, bt  
        for child in childs:
            child_minsize = child._get_minsize()
            flag = child.prop["align_flag"]
            if flag & child.BFH_SCALE:
                aim_size_x = child_minsize.x+each
            else:
                aim_size_x = child_minsize.x
            
            if flag & child.BFH_LEFT and flag & child.BFH_RIGHT:
                size_x = aim_size_x
            else:
                size_x = child_minsize.x

            if flag & child.BFV_TOP and flag & child.BFV_BOTTOM:
                size_y = aim_size_y    
            else:
                size_y = child_minsize.y

            child._sized(Vector(size_x, size_y))

            # pos
            if flag & child.BFH_LEFT and flag & child.BFH_RIGHT:
                pos_x = x
            elif flag & child.BFH_LEFT:
                pos_x = x
            elif flag & child.BFH_RIGHT:
                pos_x = x+aim_size_x- size_x
            else:
                pos_x = x+(aim_size_x- size_x)*0.5
            x += aim_size_x+gap

            if flag & child.BFV_TOP and flag & child.BFV_BOTTOM:
                pos_y = y
            elif flag & child.BFV_TOP:
                pos_y = y
            elif flag & child.BFV_BOTTOM:
                pos_y = y+aim_size_y- size_y
            else:
                pos_y = y+(aim_size_y- size_y)*0.5

            child.position = Vector(pos_x, pos_y)
            child.dirty_flag.set_flag(self.DIRTYFLAGS_MATRIX)
            child.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

class VBoxContainer(BoxContainer):

    def __init__(self, position=Vector(), size=Vector(), gap=10, border=[10,10,10,10]):
        super().__init__(position, size, gap, border)

    def _get_minsize(self):
        childs = self.get_children()
        gap = self.prop['gap']
        bl, bt, br, bb = self.prop["border"]
        minsize = Vector()
        xmax = 0
        for child in childs:
            child_minsize = child._get_minsize()
            minsize.y += child_minsize.y
            xmax = max(xmax, child_minsize.x)
        minsize.x = xmax + bl + br
        minsize.y += bt + bb + gap*(len(childs)-1)
        self.prop['minsize'] = minsize
        return minsize

    def _align(self):
        minsize = self._get_minsize()
        left_size = self.size - minsize
        childs = self.get_children()   
        gap = self.prop['gap']
        bl, bt, br, bb = self.prop["border"]

        # scale
        scale_counter = 0
        aim_size_x = minsize.x-bl-br
        for child in childs:
            child.offset = child.ALIGNMENT_LEFT_TOP
            if child.prop["align_flag"] & child.BFV_SCALE:
                scale_counter += 1
            if child.prop["align_flag"] & child.BFH_SCALE:
                aim_size_x = self.size.x-bl-br
        each = left_size.y/float(scale_counter) if scale_counter>0 else 0
        
        # 
        x, y = bl, bt  
        for child in childs:
            child_minsize = child._get_minsize()
            flag = child.prop["align_flag"]
            if flag & child.BFV_SCALE:
                aim_size_y = child_minsize.y+each
            else:
                aim_size_y = child_minsize.y
            
            if flag & child.BFV_TOP and flag & child.BFV_BOTTOM:
                size_y = aim_size_y    
            else:
                size_y = child_minsize.y

            if flag & child.BFH_LEFT and flag & child.BFH_RIGHT:
                size_x = aim_size_x
            else:
                size_x = child_minsize.x

            child._sized(Vector(size_x, size_y))

            # pos
            if flag & child.BFH_LEFT and flag & child.BFH_RIGHT:
                pos_x = x
            elif flag & child.BFH_LEFT:
                pos_x = x
            elif flag & child.BFH_RIGHT:
                pos_x = x+(aim_size_x- size_x)
            else:
                pos_x = x+(aim_size_x- size_x)*0.5
            

            if flag & child.BFV_TOP and flag & child.BFV_BOTTOM:
                pos_y = y
            elif flag & child.BFV_TOP:
                pos_y = y
            elif flag & child.BFV_BOTTOM:
                pos_y = y+(aim_size_y- size_y)
            else:
                pos_y = y+(aim_size_y- size_y)*0.5
            y += aim_size_y+gap

            child.position = Vector(pos_x, pos_y)
            child.dirty_flag.set_flag(self.DIRTYFLAGS_MATRIX)
            child.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)


######################### GraphicsItem NODES

class SimpelTextItem(BaseGraphicsItem):

    FONT_DEFAULT = c4d.FONT_DEFAULT
    FONT_STANDARD = c4d.FONT_STANDARD
    FONT_BOLD = c4d.FONT_BOLD
    FONT_MONOSPACED = c4d.FONT_MONOSPACED
    FONT_BIG = c4d.FONT_BIG
    FONT_BIG_BOLD = c4d.FONT_BIG_BOLD
    FONT_ITALIC = c4d.FONT_ITALIC

    COLOR_TRANS = c4d.COLOR_TRANS

    def __init__(self, text="Defualt", position=Vector()):
        """
        简单文字对象

        :param text: 显示的文字内容, defaults to "Defualt"
        :type text: str, optional
        :param position: 位置, defaults to Vector()
        :type position: c4d.Vector, optional
        """
        super().__init__()
        self.position = position
        self.prop["text"] = text
        self.prop["color"] = Vector(1)
        self.prop["set_font"] = self.FONT_DEFAULT
        self.prop["color_text_bg"] = self.COLOR_TRANS
        self.prop["text_rotation"] = 0
        self.prop["clip_to_frame"] = False
        self.prop["auto_fit_size"] = True
    

    def _draw(self, ua):
        pos = self.get_global_position()
        w = ua.DrawGetTextWidth(self.prop["text"])
        h = ua.DrawGetFontHeight()
        offset_x, offset_y = self.offset[0]*w, self.offset[1]*h
        self.size = Vector(w,h)
        self.prop['minsize'] = Vector(w,h)

        ua.DrawSetOpacity(self.prop["opacity"])
        ua.DrawSetFont(self.prop["set_font"])
        ua.DrawSetTextCol(self.prop["color"], self.prop["color_text_bg"])
        ua.DrawSetTextRotation(self.prop["text_rotation"])
        ua.DrawText(self.prop["text"], int(pos[0]-offset_x), int(pos[1]-offset_y), flags=c4d.DRAWTEXT_STD_ALIGN)
        ua.DrawSetTextRotation(0)


class ClipMapTextItem(BaseGraphicsItem):
    """支持缩放的Text对象"""

    def __init__(self, text="Defualt", font_size=72, position=Vector(), size=Vector(1, 1)):
        super().__init__()
        self.position = position
        self.size = size
        self.prop["text"] = text
        self.prop["color"] = Vector(1)
        self.prop["color_text_bg"] = self.DEFUALT_COLOR
        self.prop["font_size"] = font_size  # 字号尺寸和像素的关系  1 font_size == 1.33 px
        self.prop["clip_to_frame"] = False
        self.prop["auto_fit_size"] = True


        self._text_size = Vector(0)
        self._bmp = None
        self.cm = c4d.bitmaps.GeClipMap()
        self.cm.Init(0, 0, bits=32)

        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)
        self.text_width_list = []
        
        
    def _update(self):
        if self.dirty_flag.has_flag(self.DIRTYFLAGS_CHANGES):
            self._bake_text()
    
    def set_change(self, text=None, font_size=None, color=None, color_text_bg=None):
        if text is not None:
            self.prop["text"] = text
        if font_size is not None:
            self.prop["font_size"] = font_size
        if color is not None:
            self.prop["color"] = color
        if color_text_bg is not None:
            self.prop["color_text_bg"] = color_text_bg
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)
    

    def get_text_clipmap_size(self):
        font_size = self.prop["font_size"]
        cm = self.cm
        cm.BeginDraw()
        cm.SetColor(255, 255, 255, alpha=255)
        bc = c4d.bitmaps.GeClipMap.GetDefaultFont(c4d.GE_FONT_DEFAULT_SYSTEM)
        cm.SetFont(bc, font_size)
        w, h = (self.cm.TextWidth(self.prop["text"]), self.cm.TextHeight())
        self.text_width_list = []
        for tx in self.prop["text"]:
            tw = self.cm.TextWidth(tx)
            self.text_width_list.append(tw)
        cm.EndDraw()
        return w, h

    def _bake_text(self):
        font_size = self.prop["font_size"]
        cm = self.cm
        # get_size
        cm.BeginDraw()
        cm.SetColor(255, 255, 255, alpha=255)
        #bc = c4d.bitmaps.GeClipMap.GetFontDescription("CourierNewPS-ItalicMT", c4d.GE_FONT_NAME_POSTSCRIPT)
        #c4d.bitmaps.GeClipMap.SetFontSize(bc, c4d.GE_FONT_SIZE_INTERNAL, 25)
        #cm.SetFont(bc, 0.0)
        bc = c4d.bitmaps.GeClipMap.GetDefaultFont(c4d.GE_FONT_DEFAULT_SYSTEM)
        cm.SetFont(bc, font_size)
        w, h = (self.cm.TextWidth(self.prop["text"]), self.cm.TextHeight())
        
        self.text_width_list = []
        for tx in self.prop["text"]:
            tw = self.cm.TextWidth(tx)
            self.text_width_list.append(tw)
        cm.EndDraw()

        # draw
        self.cm.Init(w, h, bits=32)
        cm.BeginDraw()
        bc = c4d.bitmaps.GeClipMap.GetDefaultFont(c4d.GE_FONT_DEFAULT_SYSTEM)
        cm.SetFont(bc, font_size)
        bg = self.prop["color_text_bg"]*255
        cm.SetColor(int(bg[0]), int(bg[1]), int(bg[2]), alpha=255)
        cm.FillRect(0, 0, w, h)
        
        cl = self.prop["color"]*255
        cm.SetColor(int(cl[0]), int(cl[1]), int(cl[2]), alpha=255)
        cm.TextAt(0, 0, self.prop["text"])
        cm.EndDraw()
        self._text_size = Vector(w, h)
        if self.prop["auto_fit_size"]:
            self.size = Vector(w, h)
            self.prop['minsize'] = Vector(w, h)
        self._bmp = cm.GetBitmap().GetClone()

    def _draw_event(self, ua, parent_region: list):
        if isinstance(self.prop["color_text_bg"], int):
            color = ua.GetColorRGB(self.prop["color_text_bg"])
            self.prop["color_text_bg"] = Vector(color["r"], color["g"], color["b"])/255.0
        return super()._draw_event(ua, parent_region)
    
    def _draw(self, ua):
        if not self._bmp:
            return 
        ua.DrawSetOpacity(self.prop["opacity"])
        w, h = self._text_size[0], self._text_size[1]
        offset_x, offset_y = self.offset[0]*w, self.offset[1]*h
        pos = self.get_global_position()
        ua.DrawBitmap(self._bmp, int(pos[0]-offset_x), int(pos[1]-offset_y), int(w), int(h), 0, 0, w=int(w), h=int(h), mode=c4d.BMP_ALLOWALPHA)


class RectItem(BaseGraphicsItem):

    LINESTYLE_NORMAL = c4d.LINESTYLE_NORMAL
    LINESTYLE_DOTTED = c4d.LINESTYLE_DOTTED
    LINESTYLE_DASHED = c4d.LINESTYLE_DASHED
    LINESTYLE_DASHED_INV = c4d.LINESTYLE_DASHED_INV
    LINESTYLE_DASHED_BIG = c4d.LINESTYLE_DASHED_BIG

    def __init__(self, position=Vector(), size=Vector(), fill=False, line_width=1, line_style=LINESTYLE_NORMAL):
        super().__init__()
        self.position = position
        self.size = size
        self.prop["fill"] = fill
        self.prop["line_width"] = line_width
        self.prop["line_style"] = line_style

    def _draw(self, ua): 
        ua.DrawSetOpacity(self.prop["opacity"])
        ua.DrawSetPen(self.prop["color"])
        if self.prop["fill"]:
            ua.DrawRectangle(*self.get_global_bbox())
        else:
            ua.DrawFrame(*self.get_global_bbox(), lineWidth=self.prop["line_width"], lineStyle=self.prop["line_style"])


class BitmapItem(BaseGraphicsItem):

    FIT_TYPE_NONE = 0  # 不做任何适配
    FIT_TYPE_FIT = 1  # 图片适配到尺寸
    FIT_TYPE_FULL = 2  # 尺寸适配到图片
    FIT_TYPE_HEIGHT = 3 # 高度适配
    FIT_TYPE_WIDTH = 4  # 宽度适配

    def __init__(self, bmp=None, position=Vector(), size=Vector()):
        super().__init__()
        self.position = position
        self.size = size
        self.prop["bitmap"] = bmp
        self.prop["fit_type"] = self.FIT_TYPE_FIT
        self.prop["color"] = None
        self.change_bmp(bmp)

        self.draw_area = None
        self.draw_map = None

    def _update(self):
        if self.dirty_flag.has_flag(self.DIRTYFLAGS_CHANGES):
            self._fit_type_changed()
        elif self.dirty_flag.has_flag(self.DIRTYFLAGS_MATRIX):
            self._fit_type_changed()

    def _fit_type_changed(self):
        bit_w, bit_h = self.bitmap_size[0], self.bitmap_size[1]
        x1, y1, x2, y2 = self.get_global_bbox()
        pos = self.get_global_position()
        size = self.size

        if self.prop["fit_type"] == self.FIT_TYPE_FIT:
            area_x, area_y = x1, y1
            area_w, area_h = size[0], size[1]
            map_x, map_y = 0, 0
            map_w, map_h = bit_w, bit_h
        elif self.prop["fit_type"] == self.FIT_TYPE_FULL:
            offset_x, offset_y = self.offset[0]*bit_w, self.offset[1]*bit_h
            area_x, area_y = pos[0]-offset_x, pos[1]-offset_y
            area_w, area_h = bit_w, bit_h
            map_x, map_y = 0, 0
            map_w, map_h = bit_w, bit_h
            self.size = Vector(area_w, area_h)

        elif self.prop["fit_type"] == self.FIT_TYPE_HEIGHT:
            scale_w = size[1]/bit_h*bit_w
            offset_x, offset_y = self.offset[0]*scale_w, self.offset[1]*size[1]
            area_x, area_y = pos[0]-offset_x, pos[1]-offset_y
            area_w, area_h = scale_w, size[1]
            map_x, map_y = 0, 0
            map_w, map_h = bit_w, bit_h

        elif self.prop["fit_type"] == self.FIT_TYPE_WIDTH:
            scale_h = size[0]/bit_w*bit_h
            offset_x, offset_y = self.offset[0]*size[0], self.offset[1]*scale_h
            area_x, area_y = pos[0]-offset_x, pos[1]-offset_y
            area_w, area_h = size[0], scale_h
            map_x, map_y = 0, 0
            map_w, map_h = bit_w, bit_h

        else: # self.FIT_TYPE_NONE
            offset_x, offset_y = self.offset[0]*bit_w, self.offset[1]*bit_h
            area_x, area_y = pos[0]-offset_x, pos[1]-offset_y
            area_w, area_h = bit_w, bit_h
            map_x, map_y = 0, 0
            map_w, map_h = bit_w, bit_h
        
        self.draw_area = [int(area_x), int(area_y), int(area_w), int(area_h)]
        self.draw_map = [int(map_x), int(map_y), int(map_w), int(map_h)]

    def change_bmp(self, bmp):
        self.bitmap_size = [0,0]
        self.prop["bitmap"] = bmp
        if bmp:
            self.bitmap_size = [bmp.GetBw(), bmp.GetBh()]     
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

    def change_size(self, size):
        self.size = size
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

    def change_fit_type(self, fit_type=FIT_TYPE_NONE):
        self.prop["fit_type"] = fit_type
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

    def _draw(self, ua):
        if not self.prop["bitmap"] or not self.draw_area:
            return 
        if self.prop["color"]:
            ua.DrawSetPen(self.prop["color"])
        ua.DrawSetOpacity(self.prop["opacity"])
        ua.DrawBitmap(self.prop["bitmap"], *self.draw_area,  # 画板中的区域
                                            *self.draw_map,  # 图片中的区域
                                            mode= c4d.BMP_ALLOWALPHA)


class BaseBezierItem(BaseGraphicsItem):
    
    LINESTYLE_NORMAL = c4d.LINESTYLE_NORMAL
    LINESTYLE_DOTTED = c4d.LINESTYLE_DOTTED
    LINESTYLE_DASHED = c4d.LINESTYLE_DASHED
    LINESTYLE_DASHED_INV = c4d.LINESTYLE_DASHED_INV
    LINESTYLE_DASHED_BIG = c4d.LINESTYLE_DASHED_BIG

    def __init__(self, position=Vector(), size=Vector(1)):
        super().__init__()
        self.position = position
        self.size = size  # 如果size为0 会因为area的绘制机制而被跳过 如果确定要设置为0 可以调用self.prop["clip_optimize"] = False

        self.prop["clip_to_frame"] = False
        self.prop["bezier_objects"] = []
        self.prop["shape_closed"] = False
        self.prop["fill"] = False
        self.prop["line_width"] = 4
        self.prop["line_style"] = self.LINESTYLE_NORMAL

        self.start_list = []
        self.points_list = []

    def _update(self):
        if self.dirty_flag.has_flag(self.DIRTYFLAGS_CHANGES):
            self.update_list()
        elif self.dirty_flag.has_flag(self.DIRTYFLAGS_MATRIX):
            self.update_list()

    def _draw(self, ua):
        if not self.start_list:
            return 
        ua.DrawSetOpacity(self.prop["opacity"])
        ua.DrawSetPen(self.prop["color"])
        if self.prop["fill"]:
            ua.DrawBezierFill(self.start_list, self.points_list, self.prop["shape_closed"])
        else:
            ua.DrawBezierLine(self.start_list, self.points_list, self.prop["shape_closed"], self.prop["line_width"], self.prop["line_style"])
  
    def get_bezier_object(self, index=0):
        return self.prop["bezier_objects"][index]

    def change_object(self, index, part, value, update=True):
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)
        bo = self.get_bezier_object(index)
        bo.change(part, value, update)

    def add_bezier_object(self, start=Vector(), end=Vector() ,start_hand_offset=Vector(), end_hand_offset=Vector(), update=False):
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)
        bezier_object = SingleBezierObject(start, end ,start_hand_offset, end_hand_offset)
        last = self.prop["bezier_objects"][-1] if self.prop["bezier_objects"] else None
        self.prop["bezier_objects"].append(bezier_object)
        if last:
            bezier_object.change("start", last.get_part("end"), update)
        return bezier_object

    def clean_all_objects(self):
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)
        self.prop["bezier_objects"] = []
        self.start_list = []
        self.points_list = []

    def update_list(self, innder_update=False):
        """ 将分散的bezier_objects合并为一个对象 并获取全局点位
        
        Args:
            innder_update : 完全刷新所有对象的点位 (若已经刷新过,设置为False可以提升效率)
        
        """
        pos = self.get_global_position()
        offset_x, offset_y = self.offset[0]*self.size[0], self.offset[1]*self.size[1]
        move_x, move_y = pos[0]-offset_x, pos[1]-offset_y
        self.start_list, self.points_list = SingleBezierObject.get_all_points(
                                                self.prop["bezier_objects"], 
                                                offset=[move_x, move_y], 
                                                innder_update=innder_update
                                                )
  

class RoundRectItem(BaseBezierItem):

    LINESTYLE_NORMAL = c4d.LINESTYLE_NORMAL
    LINESTYLE_DOTTED = c4d.LINESTYLE_DOTTED
    LINESTYLE_DASHED = c4d.LINESTYLE_DASHED
    LINESTYLE_DASHED_INV = c4d.LINESTYLE_DASHED_INV
    LINESTYLE_DASHED_BIG = c4d.LINESTYLE_DASHED_BIG

    def __init__(self, position=Vector(), size=Vector(), radius=15, round_offset=0.43, fill=False, line_width=2, line_style=LINESTYLE_NORMAL):
        super().__init__()
        self.position = position
        self.size = size
        self.prop["raidus"] = radius
        self.prop["sperate_radius"] = [None, None, None, None]
        self.prop["round_offset"] = round_offset
        self.prop["fill"] = fill
        self.prop["line_width"] = line_width
        self.prop["line_style"] = line_style
        self.prop["shape_closed"] = True
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

    def _update(self):
        if self.dirty_flag.has_flag(self.DIRTYFLAGS_CHANGES):
            self.get_rect()
        if self.dirty_flag.has_flag(self.DIRTYFLAGS_MATRIX):
            self.update_list()

    def set_radius(self, radius):
        self.prop["raidus"] = radius
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

    def set_seperate_radius(self, lt=None, rt=None, rb=None, lb=None):
        self.prop["sperate_radius"] = [lt, rt, rb, lb]
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

    def get_rect(self):
        """获取由bezier_object组成的倒角矩形
        """
        size = self.size
        self.clean_all_objects()
        all_radius = self.prop["raidus"]
        round_offset = (1-self.prop["round_offset"])
        all_rad = all_radius *round_offset
        lt, rt, rb, lb = self.prop["sperate_radius"]
        # lt
        if lt is None:
            radius, rad = all_radius, all_rad
        else:
            radius = lt
            rad = radius *round_offset
        self.add_bezier_object(start=Vector(0, radius), end=Vector(radius, 0) ,start_hand_offset=Vector(0,-rad), end_hand_offset=Vector(-rad,0))
        
        # rt
        if rt is None:
            radius, rad = all_radius, all_rad
        else:
            radius = rt
            rad = radius *round_offset
        self.add_bezier_object(end=Vector(size[0], 0)-Vector(radius, 0) ,start_hand_offset=Vector(), end_hand_offset=Vector())
        self.add_bezier_object(end=Vector(size[0], 0)+Vector(0, radius) ,start_hand_offset=Vector(rad,0), end_hand_offset=Vector(0,-rad))
        
        # rb
        if rb is None:
            radius, rad = all_radius, all_rad
        else:
            radius = rb
            rad = radius *round_offset
        self.add_bezier_object(end=Vector(size[0], size[1])-Vector(0, radius) ,start_hand_offset=Vector(), end_hand_offset=Vector())
        self.add_bezier_object(end=Vector(size[0], size[1])-Vector(radius, 0) ,start_hand_offset=Vector(0,rad), end_hand_offset=Vector(rad,0))
        
        
        # lb
        if lb is None:
            radius, rad = all_radius, all_rad
        else:
            radius = lb
            rad = radius *round_offset
        self.add_bezier_object(end=Vector(0, size[1])+Vector(radius, 0) ,start_hand_offset=Vector(), end_hand_offset=Vector())
        self.add_bezier_object(end=Vector(0, size[1])-Vector(0, radius) ,start_hand_offset=Vector(-rad,0), end_hand_offset=Vector(0,rad))

        self.update_list(innder_update=True) 
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)
        
    def change_size(self, size):
        self.size = size
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

######################### Main

class AdvanceUserArea(Node2D):

    def __init__(self):
        super().__init__()
        self.viewport_size_changed = Signal(List) # called when window size changed
        self.scrollgroup_offsetchanged = Signal() # called when window scrolled

        self.bg_color = c4d.COLOR_BG
        self.draw_debug_frames = False

        self.ua = CoreGeUserArea(self)

    def set_min_size(self, size):
        self.ua.min_size = size
        self.set_redraw(layout_changed=True)

    def set_redraw(self, layout_changed=False):
        """
        想要手动重绘制ua时调用该方法

        .. warning::
            注意：刷新方法尽量使用该函数，如果是高级开发者，想要直接使用 AUA.ua.Redraw() 或者 AUA.ua.LayoutChanged() 方法的，
            请勿在 DrawMsg 函数调用过程中使用，否则会导致C4D陷入死循环而崩溃。比如 Node._update方法默认在 DrawMsg 过程调用。

        :param layout_changed: 界面尺寸发生改变时设置为True, defaults to False
        :type layout_changed: bool, optional
        """
        if not layout_changed:
            self.ua._set_redraw()
        else:
            self.ua._set_layout_changed()  

    def convert_colorid_to_vector(self, colorid:int):
        color = self.ua.GetColorRGB(colorid)
        return Vector(color["r"], color["g"], color["b"])/255.0

    def get_scroll_area_value(self, scroll_group_id):
        return self.ua.GetDialog().GetVisibleArea(scroll_group_id)

    def _draw(self, ua):
        ua.DrawSetPen(self.bg_color)
        ua.DrawRectangle(*ua._view)
        














