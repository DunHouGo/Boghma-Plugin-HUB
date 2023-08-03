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
importlib.reload(ualib.utils)
from ualib.core import *


class SingleLineItem(RectItem):

    def __init__(self):
        super().__init__()
        self.prop["color"] = Vector(0.3)
        self.prop["fill"] = True
        self.item_list = []
        self.user_flag.init_flag(["auto_align"])
        self.indent = 1
        self.user_flag.set_flag("auto_align")
        self.indent_space = 10
        self.focusable = True

    def _update(self):
        super()._update()
        if self.user_flag.has_flag("auto_align"):
            self.align()

    def set_size(self, size):
        self.size = size 
        self.align()


    def set_bg_color(self, color, temp=False):
        self.prop["color"] = color
        if not temp:
            self.temp_color = color
        for text in self.item_list:
            if isinstance(text, ClipMapTextItem):
                text.set_change(color_text_bg=color)

    def add_text_item(self, text, font_size=24):
        self.user_flag.set_flag("auto_align")
        item = ClipMapTextItem(str(text), font_size)
        item.set_change(color_text_bg=self.prop["color"])
        item.insert_underlast(self)
        item.offset = item.ALIGNMENT_LEFT_MID
        self.item_list.append(item)

    def add_bitmap_item(self, bmp):
        self.user_flag.set_flag("auto_align")
        item = BitmapItem(bmp)
        item.insert_underlast(self)
        item.offset = item.ALIGNMENT_LEFT_MID
        self.item_list.append(item)

    def get_item(self, index):
        self.user_flag.set_flag("auto_align")
        return self.item_list[index]

    def remove_item(self, index):
        self.user_flag.set_flag("auto_align")
        item = self.item_list[index]
        item.remove()
        self.item_list.remove(item)

    def align(self):
        size = self.size
        x = self.indent *self.indent_space
        y = 0
        space = 5
        for item in self.item_list:
            item.position = Vector(x, size[1]*0.5)
            x += space + item.size[0]
    
    def _mouse_enter_event(self, event: BaseEvent):
        if not self.focusable:
            return 
        self.set_bg_color(c4d.COLOR_BGFOCUS, temp=True)
        event.set_redraw()

    def _mouse_leave_event(self, event: BaseEvent):
        if not self.focusable:
            return 
        self.set_bg_color(self.temp_color)
        event.set_redraw()

class SingleLineView(RectItem):

    def __init__(self):
        super().__init__()
        self.prop["color"] = c4d.COLOR_BG
        self.prop["fill"] = True

        self.font_size = 24

        self._drag_item = None

        ##
        header = SingleLineItem()
        header.add_text_item("Title", self.font_size)
        header.insert_underlast(self)
        header.set_bg_color(c4d.COLOR_BG_TAB_BAR)
        header.focusable = False
        
        self.header = header
        text = header.get_item(0)
        self.tw, self.th = text.get_text_clipmap_size()
        
        self.single_items = []
        for i in range(10):
            single_item = SingleLineItem()
            single_item.add_text_item("test"+str(i), self.font_size)
            single_item.insert_underlast(self)
            single_item.indent = 2
            self.single_items.append(single_item)

        self.align()
    
    def align(self):
        self.header.set_size(Vector(self.size[0], self.th+10))
        x = self.header.position[0]
        y = self.header.size[1]
        for index, item in enumerate(self.single_items):
            item.position = Vector(x, y)
            item.set_size(Vector(self.size[0], self.th+5))
            if index%2 == 0:
                item.set_bg_color(c4d.COLOR_BG_DARK1)
            else:
                item.set_bg_color(c4d.COLOR_BG_DARK2)
            y += item.size[1]

    def rearange(self):
        self.single_items.sort(key=lambda x: x.position[1])
        self.align()
        

    def get_item(self, x, y):
        for item in self.single_items: 
            if item.is_point_inside(x, y):
                item.remove()
                item.insert_under(self)
                return item

    def _on_size_changed(self, size):
        self.size = Vector(size[0]*0.5, size[1])
        self.align()

    def _mouse_press_event(self, event: BaseEvent):
        self.prop["focus"] = True
        if event.is_mouse_left_pressed():
            x, y = event.get_mouse_pos()
            item = self.get_item(x, y)
            if item: 
                item.set_bg_color(c4d.COLOR_BGFOCUS, temp=True)
                self._drag_item = item
                self._start_position = item.position
            self.start_drag_event(event)

    def _mouse_drag_start_event(self, event: BaseEvent):
        pass
    
    def _mouse_drag_process_event(self, event: BaseEvent):
        if self._drag_item: 
            item = self._drag_item
            sx, sy = event["mouse_down_position"]
            dx, dy = event["mouse_hold_position"]
            aim = self._start_position+Vector(dx-sx, dy-sy)
            item.position += (aim-item.position)*self._drag_mouse_follow
            item.position.x = 0
            event.set_redraw()

    def _mouse_drag_release_event(self, event: BaseEvent):
        if self._drag_item: 
            self._drag_item = None
            self.rearange()
            event.set_redraw()

class G4D_Test_MainDlg(c4d.gui.GeDialog):

    ID_GROUP_NONE = 1000
    ID_Group_Scroll = 1001

    def __init__(self):
        self.AUA = AdvanceUserArea()
        #self.AUA.draw_debug_frames = 1

        root = self.AUA
        slv = SingleLineView()
        slv.insert_under(root)
        root.viewport_size_changed.connect(slv._on_size_changed)


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
        return True

    def Command(self, id, msg):
        return True

    def Message(self, msg, result):
        return c4d.gui.GeDialog.Message(self, msg, result)



if __name__ == '__main__':
    dialog = G4D_Test_MainDlg()
    dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=0, xpos=-2, ypos=-2, defaultw=800, defaulth=800, subid=0)