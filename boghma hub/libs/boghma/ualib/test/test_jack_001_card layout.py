import c4d
import os
import sys
import importlib

SCRIPTPATH = os.path.dirname(__file__)
Lib_Path = os.path.dirname(os.path.dirname(SCRIPTPATH))

if Lib_Path not in sys.path:
    sys.path.append(Lib_Path)

import ualib
importlib.reload(ualib)
from ualib.core import *


BMP = ualib.utils.get_bitmap_from(r"G:\灵感\celeste.jpg")

class CardItem(RoundRectItem):

    def __init__(self, name="", position=Vector(10,10), size=Vector(160, 180)):
        super().__init__()
        self.pressed = Signal()
        self.name = name
        self.position = position
        self.size = size
        

        self.prop["moveable"] = False
        self.init()
        self.user_flag.init_flag(["init_bitmap"])
        self.user_flag.set_flag("init_bitmap")

    def init(self):
        size = self.size
        text_height = 20
        border = 10

        item = SimpelTextItem(text=self.name)
        item.position = Vector(border+5, border)
        item.size = Vector(size[0], text_height)
        item.insert_underlast(self)
        self.text = item

        item = BitmapItem(BMP)
        item.offset = self.ALIGNMENT_CENTER
        w = size[0]-border*2
        item.position = Vector(size[0]*0.5, w*0.5 +text_height+border)
        item.size = Vector(w,w)
        item.insert_underlast(self)
        self.temp_size = Vector(w,w)

        self.bmp = item

    def _update(self):
        super()._update()  # 一定要有 否则矩形无法刷新

        if self.user_flag.has_flag("init_bitmap"):
            BMP2 = ualib.utils.get_bitmap_from(r"G:\灵感\t1.jpg")  # 在这里初始化新的图把路径传进来
            self.bmp.change_bmp(BMP2)

    def _mouse_enter_event(self, event: BaseEvent):
        """
        :meta public:

        鼠标进入事件在这里执行
        """
        self.prop["line_width"] = 4
        self.bmp.change_size(self.temp_size*0.9)
        #event.set_handled()
        event.set_redraw()

    def _mouse_leave_event(self, event: BaseEvent):
        """
        :meta public:

        鼠标离开事件在这里执行
        """
        self.prop["line_width"] = 2
        self.bmp.change_size(self.temp_size)
        #event.set_handled()
        event.set_redraw()

    def _mouse_press_event(self, event: BaseEvent):
        if event.is_mouse_left_pressed():
            self.pressed.emit(self, True)
        if event.is_mouse_right_pressed():
            self.pressed.emit(self, False)
        return super()._mouse_press_event(event)

class Scene(Node2D):

    def __init__(self, aua):
        super().__init__()

        self.insert_under(aua)
        aua.viewport_size_changed.connect(self._on_viewport_size_changed)
        self.minsize_changed = Signal(Vector)
        self.minsize_changed.connect(aua.set_min_size)

        self.win_size = Vector()
        self.user_flag.init_flag(["custom_flag"])

    def _update(self):
        if self.user_flag.has_flag("custom_flag"):
            self.align()

    def new_card(self, name):
        self.user_flag.set_flag("custom_flag")
        card = CardItem(name)
        card.pressed.connect(self._on_card_pressed)
        card.insert_underlast(self)
        return card

    def align(self):
        children = self.get_children()
        if not children:
            return
        space = [10, 10]
        x = space[0]
        y = space[1]
        count = 0
        for child in children:
            count += 1
            child.position = Vector(x, y)
            incr = child.size[0]+space[0]
            x += incr
            if x > self.win_size[0] - incr:
                y += child.size[1]+space[1]
                x = space[0]

        minsize = Vector()
        if children:
            pos = children[-1].get_global_position()
            minsize.y = pos[1]+children[-1].size[1]+space[1]
        self.minsize_changed.emit(minsize)

    def _on_viewport_size_changed(self, size):
        self.win_size = Vector(size[0], size[1])
        self.user_flag.set_flag("custom_flag")

    def _on_card_pressed(self, card, is_left):
        print(card.name, "is pressed", is_left)


class G4D_Test_MainDlg(c4d.gui.GeDialog):

    ID_GROUP_NONE = 1000
    ID_Group_Scroll = 1001

    def __init__(self):
        self.AUA = AdvanceUserArea()
        self.scene = Scene(self.AUA)

    def CreateLayout(self):
        self.SetTitle("ualibe TEST")
        if self.GroupBegin(self.ID_GROUP_NONE, c4d.BFH_SCALEFIT| c4d.BFV_SCALEFIT, cols=1, rows=0, title="", groupflags=0, initw=0, inith=0):
            self.GroupBorderSpace(10, 5, 10, 10)
            if self.ScrollGroupBegin(self.ID_Group_Scroll, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, scrollflags=c4d.SCROLLGROUP_VERT | c4d.SCROLLGROUP_AUTOVERT):
                self.AddUserArea(100, c4d.BFH_SCALEFIT| c4d.BFV_SCALEFIT, initw=0, inith=0)
                self.AttachUserArea( self.AUA.ua, 100)
            self.GroupEnd()
        self.GroupEnd()
        return True

    def InitValues(self):
        self.scene.remove_all_children()
        for i in range(100):
            card = self.scene.new_card("card"+str(i))

        return True

    def Command(self, id, msg):
        return True

    def Message(self, msg, result):
        return c4d.gui.GeDialog.Message(self, msg, result)



if __name__ == '__main__':
    dialog = G4D_Test_MainDlg()
    dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=0, xpos=-2, ypos=-2, defaultw=800, defaulth=800, subid=0)