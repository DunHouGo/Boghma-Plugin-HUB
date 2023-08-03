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


BMP = ualib.utils.get_bitmap_from(os.path.join(SCRIPTPATH,"ninepitch","test.png"))

class Nipitch(BaseGraphicsItem):

    def __init__(self, name="", position=Vector(10,10), size=Vector(50, 50)):
        super().__init__()
        self.name = name
        self.position = position
        self.size = size
        self.prop["bitmap"] = BMP
        self.prop["slice"] = [50,50,50,50]
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)
        self.draw_list = []

    def _update(self):
        if self.dirty_flag.has_flag(self.DIRTYFLAGS_CHANGES):
            self.main_fun()
        elif self.dirty_flag.has_flag(self.DIRTYFLAGS_MATRIX):
            self.main_fun()
    def main_fun(self):
        self.draw_list = []
        w, h = self.prop["bitmap"].GetBw(), self.prop["bitmap"].GetBh()
        x1, y1, x2, y2 = self.get_global_bbox()
        left, top, right, bottom = self.prop["slice"]
        midwidth = (x2-x1)-left-right
        midheight = (y2-y1)-top-bottom
        bmp_midwidth = w-left-right
        bmp_height = h-top-bottom


        # 1
        draw_area = [x1, y1, left, top] # x, y, w, h
        bmp_area = [0 , 0, left, top] # x, y, w, h
        self.draw_list.append([draw_area, bmp_area])
        # 2 
        draw_area = [x1+left, y1, midwidth, top] # x, y, w, h
        bmp_area = [left, 0, bmp_midwidth, top] # x, y, w, h
        self.draw_list.append([draw_area, bmp_area])
        # 3
        draw_area = [x2-right, y1, right, top] # x, y, w, h
        bmp_area = [w-right, 0, right, top] # x, y, w, h
        self.draw_list.append([draw_area, bmp_area])

        # 4
        draw_area = [x1, y1+top, left, midheight] # x, y, w, h
        bmp_area = [0 , top, left, bmp_height] # x, y, w, h
        self.draw_list.append([draw_area, bmp_area])
        # 5 
        draw_area = [x1+left, y1+top, midwidth, midheight] # x, y, w, h
        bmp_area = [left, top, bmp_midwidth, bmp_height] # x, y, w, h
        self.draw_list.append([draw_area, bmp_area])
        # 6
        draw_area = [x2-right, y1+top, right, midheight] # x, y, w, h
        bmp_area = [w-right, top, right, bmp_height] # x, y, w, h
        self.draw_list.append([draw_area, bmp_area])

        # 7
        draw_area = [x1, y2-bottom, left, bottom] # x, y, w, h
        bmp_area = [0 , h-bottom, left, bottom] # x, y, w, h
        self.draw_list.append([draw_area, bmp_area])
        # 8 
        draw_area = [x1+left, y2-bottom, midwidth, bottom] # x, y, w, h
        bmp_area = [left, h-bottom, bmp_midwidth, bottom] # x, y, w, h
        self.draw_list.append([draw_area, bmp_area])

        # 9 
        draw_area = [x2-right, y2-bottom, right, bottom] # x, y, w, h
        bmp_area = [w-right, h-bottom, right, bottom] # x, y, w, h
        self.draw_list.append([draw_area, bmp_area])


    def _draw(self, ua):
        if not self.prop["bitmap"]:
            return 

        for draw_area, bmp_area in self.draw_list:
            ua.DrawBitmap(self.prop["bitmap"], *draw_area,  # 画板中的区域
                                                *bmp_area,  # 图片中的区域
                                                mode=c4d.BMP_ALLOWALPHA)

class G4D_Test_MainDlg(c4d.gui.GeDialog):

    ID_GROUP_NONE = 1000
    ID_Group_Scroll = 1001

    def __init__(self):
        self.AUA = AdvanceUserArea()
        root = self.AUA
        #self.AUA.ua.draw_debug_frames = 1

        # 三层 rect
        parent = root
        item = Nipitch(position=Vector(10), size=Vector(500, 500))
        item.prop["moveable"] = True
        item.insert_under(parent)


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