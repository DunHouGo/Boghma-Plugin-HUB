import math
import copy
from typing import Callable, Union, List

import c4d
from c4d import Vector



def get_bitmap_from(source)->c4d.bitmaps.BaseBitmap:
    """通过输入图片路径或者c4d icon id来返回对应的 bitmap对象

    Args:
        source (int or str): 对应参数

    Returns:
        c4d.bitmaps.BaseBitmap: 
    """
    if isinstance(source, str):
        bmp = c4d.bitmaps.BaseBitmap()
        result, isMovie = bmp.InitWith(source)
        if result == c4d.IMAGERESULT_OK: 
            return bmp
    elif isinstance(source, int):
        bmp = c4d.bitmaps.InitResourceBitmap(source)
        return bmp

def set_mouse_pointer(name):
    """
    | 这样用 set_mouse_pointer("MOUSE_HIDE")
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
    c4d.gui.SetMousePointer(eval(f"c4d.{name}"))

class BaseHierarchy:
    """一个用于管理父子级关系的基类。"""

    def __init__(self):
        super().__init__()
        self.hierarchy_changed = Signal()
        self._parent = None
        self._children = []

    def get_children(self):
        """获取该节点的子节点列表。"""
        return copy.copy(self._children)

    def get_down(self):
        """获取第一个子节点。"""
        if self._children:
            return self._children[0]

    def get_downlast(self):
        """获取最后一个子节点。"""
        if self._children:
            return self._children[-1]

    def get_next(self):
        """获取下一个兄弟节点。"""
        if self._parent and self._parent._children:
            index = self._parent._children.index(self)
            if index + 1 != len(self._parent._children):
                return self._parent._children[index + 1]

    def get_pred(self):
        """获取前一个兄弟节点。"""
        if self._parent and self._parent._children:
            index = self._parent._children.index(self)
            if index != 0:
                return self._parent._children[index - 1]

    def get_up(self):
        """获取父节点。"""
        return self._parent

    def insert_after(self, obj):
        """在指定节点之后插入该节点。"""
        if obj and obj._parent and obj != self:
            index = obj._parent._children.index(obj)
            obj._parent._children.insert(index + 1, self)
            self._parent = obj._parent
            self._hierarchy_changed()
            return True
        else:
            return False

    def insert_before(self, obj):
        """在指定节点之前插入该节点。"""
        if obj and obj._parent and obj != self:
            index = obj._parent._children.index(obj)
            obj._parent._children.insert(index, self)
            self._parent = obj._parent
            self._hierarchy_changed()
            return True
        else:
            return False

    def insert_under(self, obj):
        """将该节点添加为指定节点的第一个子节点。"""
        if obj and obj != self:
            obj._children.insert(0, self)
            self._parent = obj
            self._hierarchy_changed()
            return True
        else:
            return False

    def insert_underlast(self, obj):
        """将该节点添加为指定节点的最后一个子节点。"""
        if obj and obj != self:
            obj._children.append(self)
            self._parent = obj
            self._hierarchy_changed()
            return True
        else:
            return False

    def iter_all_children(self):
        """获取该节点的所有子孙节点的生成器。"""
        for obj in self.get_children():
            yield obj
            for obj2 in obj.iter_all_children():
                yield obj2

    def remove(self):
        """从父节点的子节点列表中移除该节点。"""
        parent = self.get_up()
        if parent:
            self._parent = None
            parent._children.remove(self)
            self._hierarchy_changed()
            return True
        else:
            return False

    def remove_all_children(self):
        """移除该节点的所有子节点。"""
        for obj in reversed(self._children):
            obj.remove()
            obj._hierarchy_changed()

    def set_parent(self, parent):
        """设置父节点。"""
        if parent != self._parent:
            if self._parent:
                self._parent._children.remove(self)
            self._parent = parent
            if self._parent:
                self._parent._children.append(self)
            self._hierarchy_changed()

    def set_children(self, children):
        """设置子节点列表。"""
        self._children = children
        for child in self._children:
            child._parent = self
        self._hierarchy_changed()

    def _hierarchy_changed(self):
        """该节点的父子级关系发生改变时发送 hierarchy_changed 信号。"""
        if self._parent:
            self._parent._hierarchy_changed()
        self.hierarchy_changed.emit()

    def _get_hierarchy(self):
        """获取该节点的层次结构，即父节点到该节点的路径列表。"""
        hierarchy = []
        node = self
        while node:
            hierarchy.insert(0, node)
            node = node._parent
        return hierarchy

    def _set_hierarchy(self, hierarchy):
        """根据层次结构列表，设置该节点的父子级关系。"""
        if len(hierarchy) > 1:
            hierarchy[-2].set_children([hierarchy[-1]])
        self.set_parent(hierarchy[-2] if len(hierarchy) > 1 else None)

    def __getstate__(self):
        """获取对象状态，用于序列化。"""
        return {"parent": self._parent, "children": self._children}

    def __setstate__(self, state):
        """设置对象状态，用于反序列化。"""
        self._parent = state["parent"]
        self._children = state["children"]
        for child in self._children:
            child._parent = self

    #parent = property(get_up, set_parent)
    #hierarchy = property(_get_hierarchy, _set_hierarchy)
    
class Signal:
    """用于模仿pyqt中的Signal类。"""

    def __init__(self, *args_types, **kwargs_types):
        self._slots = []
        # 类型检查会报错 继承的instance类型无法匹配 所以先禁用
        #self._args_types = args_types
        #self._kwargs_types = kwargs_types

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
        # if self._args_types:
        #     if len(args) != len(self._args_types):
        #         raise TypeError(f"Expected {len(self._args_types)} argument(s), but got {len(args)}")

        #     for i, arg_type in enumerate(self._args_types):
        #         if not isinstance(args[i], arg_type):
        #             raise TypeError(f"Expected argument {i+1} to be of type {arg_type}, but got {type(args[i])}")

        # if self._kwargs_types:
        #     for kwarg_name, kwarg_type in self._kwargs_types.items():
        #         if kwarg_name not in kwargs:
        #             raise TypeError(f"Expected keyword argument '{kwarg_name}' not found")

        #         if not isinstance(kwargs[kwarg_name], kwarg_type):
        #             raise TypeError(f"Expected keyword argument '{kwarg_name}' to be of type {kwarg_type}, but got {type(kwargs[kwarg_name])}")

        for slot in self._slots:
            slot(*args, **kwargs)

class SimpleFlag:
    """标志位类，用于管理和操作多个二进制标志位。

    Attributes:
        flags (int): 所有标志位的值。
        flag_names (List[str]): 所有标志位的名称。

    """

    def __init__(self, flag_names: List[str]=[]) -> None:
        """初始化标志位类。

        Args:
            flag_names: 所有标志位的名称列表。

        """
        self.flags = 0
        self.init_flag(flag_names)

    def init_flag(self, flag_names: List[str]):
        self.flag_names = flag_names
        for i, name in enumerate(flag_names):
            setattr(self, name, 1 << i)

    def set_flag(self, flag: Union[str, int]) -> None:
        """设置指定的标志位。

        Args:
            flag: 标志位的名称或位置。

        """
        if isinstance(flag, str):
            flag = getattr(self, flag)
        self.flags |= flag

    def clear_flag(self, flag: Union[str, int]) -> None:
        """清除指定的标志位。

        Args:
            flag: 标志位的名称或位置。

        """
        if isinstance(flag, str):
            flag = getattr(self, flag)
        self.flags &= ~flag

    def toggle_flag(self, flag: Union[str, int]) -> None:
        """切换指定的标志位。

        Args:
            flag: 标志位的名称或位置。

        """
        if isinstance(flag, str):
            flag = getattr(self, flag)
        self.flags ^= flag

    def has_flag(self, flag: Union[str, int]) -> bool:
        """检查是否存在指定的标志位。

        Args:
            flag: 标志位的名称或位置。

        Returns:
            bool: True表示存在该标志位，False表示不存在。

        """
        if isinstance(flag, str):
            flag = getattr(self, flag)
        return bool(self.flags & flag)

    def clear_all_flags(self) -> None:
        """清除所有标志位。"""
        self.flags = 0

    def get_flag_names(self) -> List[str]:
        """获取所有标志位的名称。

        Returns:
            List[str]: 所有标志位的名称列表。

        """
        return self.flag_names

    def get_flag_positions(self) -> List[int]:
        """获取所有标志位的位置。

        Returns:
            List[int]: 所有标志位的位置列表。

        """
        return [i for i in range(len(self.flag_names))]

    def get_flag_by_position(self, position: int) -> str:
        """通过位置获取标志位的名称。

        Args:
            position: 标志位的位置。

        Returns:
            str: 标志位的名称。

        """
        return self.flag_names[position]


class BaseFrame(BaseHierarchy):
    """ 
    | 基础区域对象,可以通过位置和尺寸来返回全局bbox属性 即: x1, y1, x2, y2
    | 可以通过set_alignment()方法或者offset, 设置中心点位置(默认在左上角)
    | 除此之外支持一些常用判定方法: 
    |     1 (x,y)点是否在该区域
    |     2 是否与区域 [x1, y1, x2, y2] 相交
    |     3 获取与区域 [x1, y1, x2, y2] 相交的区域 [ox1, oy1, ox2, oy2]
    |     ...
    """
    
    ALIGNMENT_LEFT_TOP = Vector(0, 0)     
    ALIGNMENT_MID_TOP = Vector(0.5, 0)   
    ALIGNMENT_RIGHT_TOP = Vector(1, 0)   
    ALIGNMENT_LEFT_MID = Vector(0, 0.5)   
    ALIGNMENT_CENTER = Vector(0.5, 0.5)  
    ALIGNMENT_RIGHT_MID = Vector(1, 0.5)  
    ALIGNMENT_LEFT_BOTTOM = Vector(0, 1)  
    ALIGNMENT_MID_BOTTOM = Vector(0.5, 1)  
    ALIGNMENT_RIGHT_BOTTOM = Vector(1, 1)  


    def __init__(self, position=Vector(), size=Vector()):
        super().__init__()
        self.global_frame_changed = Signal()

        self._position = position
        self._size = Vector()
        self._offset = Vector()

    @property
    def position(self):
        return self._position
    
    @position.setter
    def position(self, value):
        if self._position != value:
            self._position = value
            self.global_frame_changed.emit()

    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        self._size = value

    @property
    def offset(self):
        return self._offset
    
    @offset.setter
    def offset(self, value):
        self._offset = value
    
    def get_global_position(self):
        parent = self.get_up()
        parent_pos = Vector() if not parent or not hasattr(parent, "get_global_position") else parent.get_global_position()
        return parent_pos +self.position
    
    def get_box_offset(self, offset=Vector()):
        """获取相对的偏移位置， 可以用于获取中心点等特殊位置"""
        return self.size^offset

    def get_global_bbox(self):
        pos = self.get_global_position() -self.get_box_offset(self.offset)
        pos2 = pos +self.size
        return int(pos[0]), int(pos[1]), int(pos2[0]-1), int(pos2[1]-1)
   
    def get_overlap_rect_with(self, x1,y1,x2,y2):
        return BaseFrame.rect_overlap(x1,y1,x2,y2, *self.get_global_bbox())
            
    def is_point_inside(self, x, y):
        x1, y1, x2, y2 = self.get_global_bbox()
        return (x1<=x and y1<=y) and (x<=x2 and y<=y2)

    def is_intersect_with(self, x1, y1, x2, y2):
        bx1, by1, bx2, by2 = self.get_global_bbox()
        return (bx1<=x2 and by1<=y2) and (bx2>=x1 and by2>=y1)

    @staticmethod
    def rect_overlap(ax1,ay1,ax2,ay2, bx1,by1,bx2,by2):
        if (bx1<=ax2 and by1<=ay2) and (bx2>=ax1 and by2>=ay1):#相交
            X1 = max(ax1,bx1)
            Y1 = max(ay1,by1)
            X2 = min(ax2,bx2)
            Y2 = min(ay2,by2)
            return X1,Y1,X2,Y2


class SingleBezierObject:
    """ 贝塞尔曲线对象
    """

    def __init__(self, start=Vector(), end=Vector(), start_hand_offset=Vector(), end_hand_offset=Vector()):
        """在C4D中为了绘制贝塞尔曲线一般需要用到 start_list 和 points_list, 使用 get_points() 获取

        Args:
            start (_type_, optional): 开始点
            end (_type_, optional): 结束点
            start_hand_offset (_type_, optional): 开始点手柄, 相对于开始点的位置
            end_hand_offset (_type_, optional): 结束点手柄, 相对于结束点的位置
        """
        super().__init__()
        self._start = start
        self._start_hand_offset = start_hand_offset  # 相对于 start 的坐标
        self._end_hand_offset = end_hand_offset  # 相对于 end 的坐标
        self._end = end
        self._attach_start = None
        self._attach_end = None
        self._start_list = []
        self._points_list = []
        
    def attach_bezier(self, bezier_object, attach_type="end"):
        """ 连接上下游 bezier_object

        Args:
            bezier_object (SingleBezierObject): SingleBezierObject
            attach_type (str, optional): "start" 或者 "end"
        """
        if attach_type == "start":
            self._attach_start = bezier_object
            bezier_object.attach_end = self
        else: # end
            self._attach_end = bezier_object
            bezier_object.attach_start = self

    def change(self, part, value, update=True):
        """修改BezierObject的参数 

        Args:
            part (str): "start", "end","start_hand_offset","end_hand_offset", 中的一个
            value (Vector): 位置数据
            update (bool): 当 update 为 True时才会更新 start_list 和 points_list 属性, 
                           若连续修改同一对象的不同part可以最后一次修改时设置True, 可以提升效率
        """
        if part in ["start","end","start_hand_offset","end_hand_offset"]:
            setattr(self, "_"+part, value)
            if part == "start" and self._attach_start:
                self._attach_start.end = value
                if update:
                    self._attach_start.update_list()
            elif part == "end" and self._attach_end:
                self._attach_end.start = value
                if update:
                    self._attach_end.update_list()
            if update:
                self.update_list()  
    
    def get_part(self, part):
        """获取BezierObject的参数 

        Args:
            part (str): "start", "end","start_hand_offset","end_hand_offset", 中的一个
        
        Returns:
            part (Vector): 四个控制点中对应part的位置
        """
        if part in ["start","end","start_hand_offset","end_hand_offset"]:
            return getattr(self, "_"+part)

    def update_list(self):
        """ 更新当前对象绘制贝塞尔曲线所需的所有点"""
        self._start_list = [self._start[0], self._start[1]]
        self._points_list = []
        for vec in [self._start+self._start_hand_offset, self._end_hand_offset+self._end, self._end]:
            self._points_list += [vec[0], vec[1]]
     
    def get_points(self, update=False):
        """ 获取当前对象绘制贝塞尔曲线所需的所有点

        Args:
            update (bool, optional): 是否刷新,若无刷新必要设为False可以提升效率

        Returns:
            start_list (list) : [start x, start y]
            points_list (list) : [other points]
        """
        if not self._start_list or not self._points_list:
            update = True
        if update:
            self.update_list()
        return self._start_list, self._points_list


    @staticmethod
    def get_all_points(bezier_object_list, offset=Vector(), innder_update=False):
        """ 将独立的bezier_objects作为一个对象获取全局点位
        
        Args:
            bezier_object_list (list) : SingleBezierObject 对象组成的列表
            offset (Vector, list) : 偏移量
            innder_update (bool): 完全刷新所有对象的点位 (若已经刷新过,设置为False可以提升效率)

        Returns:
            start_list (list) : [start x, start y]
            points_list (list) : [other points]
        """
        start_list = []
        points_list = []
        move_x, move_y = offset[0], offset[1]
        # 获取对所有点位进行偏移后的位置 但不改变原始对象值
        for index, bo in enumerate(bezier_object_list):
            bo_start_list, bo_points_list = bo.get_points(innder_update)
            if index == 0:
                start_list = [bo_start_list[0]+move_x, bo_start_list[1]+move_y]
            for index in range(0, len(bo_points_list),2):
                x1 = bo_points_list[index]+move_x
                y1 = bo_points_list[index+1]+move_y
                points_list += [x1, y1]
        return start_list, points_list



