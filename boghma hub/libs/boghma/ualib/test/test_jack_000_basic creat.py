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



class G4D_Test_MainDlg(c4d.gui.GeDialog):

    ID_GROUP_NONE = 1000
    ID_Group_Scroll = 1001

    def __init__(self):
        self.AUA = AdvanceUserArea()
        self.AUA.draw_debug_frames = False

        root = self.AUA

        # 三层 rect
        parent = root
        item = RectItem(position=Vector(10), size=Vector(300,200))
        item.prop["moveable"] = True
        item.insert_under(parent)

        parent = item
        item = RectItem(position=Vector(40), size=Vector(100,100))
        item.prop["moveable"] = True
        item.insert_under(parent)

        parent = item
        item = RectItem(position=Vector(50), size=Vector(80,80))
        item.prop["moveable"] = True
        item.insert_under(parent)

        # SimpelTextItem
        parent = root
        item = SimpelTextItem(text="SimpelTextItem", position=Vector(340,10))
        item.prop["moveable"] = True
        item.insert_under(parent)

        # ClipMapTextItem
        parent = root
        item = ClipMapTextItem(text="ClipMapTextItem", font_size=72, position=Vector(10,220))
        item.prop["moveable"] = True
        item.insert_under(parent)

        # BitmapItem
        BMP = ualib.utils.get_bitmap_from(r"G:\灵感\celeste.jpg")
        parent = root
        item = BitmapItem(bmp=BMP, position=Vector(10,320), size=Vector(300,200))
        item.prop["moveable"] = True
        item.insert_under(parent)

        # BaseBezierItem
        parent = root
        item = BaseBezierItem(position=Vector(340,40), size=Vector(20))
        item.add_bezier_object(start=Vector(0), end=Vector(100) ,start_hand_offset=Vector(100,0), end_hand_offset=Vector(-100,0), update=True)
        item.prop["moveable"] = True
        item.insert_under(parent)

        # RoundRectItem
        parent = root
        item = RoundRectItem(position=Vector(320,320), size=Vector(100))
        item.prop["moveable"] = True
        item.insert_under(parent)

        # RoundRectItem
        parent = root
        item = RoundRectItem(position=Vector(440,320), size=Vector(100), radius=50)
        item.prop["moveable"] = True
        item.insert_under(parent)

        # RoundRectItem
        parent = root
        item = RoundRectItem(position=Vector(440,420), size=Vector(100), radius=50)
        item.prop["moveable"] = True
        item.set_seperate_radius(lt=12, rt=22, rb=32, lb=52)
        item.insert_under(parent)
        # RoundRectItem
        parent = root
        item = RoundRectItem(position=Vector(440,520), size=Vector(100, 50), radius=50)
        item.prop["moveable"] = True
        item.set_seperate_radius(lt=20, rt=20, rb=0, lb=0)
        item.insert_under(parent)

    def CreateLayout(self):
        self.SetTitle("ualibe TEST")
        if self.GroupBegin(self.ID_GROUP_NONE, c4d.BFH_SCALEFIT| c4d.BFV_SCALEFIT, cols=1, rows=0, title="", groupflags=0, initw=0, inith=0):
            self.GroupBorderSpace(10, 5, 10, 10)
            self.AddCheckbox(200, c4d.BFH_SCALEFIT, 0,0, "show debug frame")
            if self.ScrollGroupBegin(self.ID_Group_Scroll, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, scrollflags=c4d.SCROLLGROUP_VERT | c4d.SCROLLGROUP_AUTOVERT):
                self.AddUserArea(100, c4d.BFH_SCALEFIT| c4d.BFV_SCALEFIT, initw=0, inith=0)
                self.AttachUserArea( self.AUA.ua, 100)
            self.GroupEnd()
        self.GroupEnd()
        return True

    def InitValues(self):
        return True

    def Command(self, id, msg):
        if id == 200:
            self.AUA.draw_debug_frames = self.GetBool(id)
            self.AUA.set_redraw()
        return True

    def Message(self, msg, result):
        return c4d.gui.GeDialog.Message(self, msg, result)



if __name__ == '__main__':
    dialog = G4D_Test_MainDlg()
    dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=0, xpos=-2, ypos=-2, defaultw=800, defaulth=800, subid=0)