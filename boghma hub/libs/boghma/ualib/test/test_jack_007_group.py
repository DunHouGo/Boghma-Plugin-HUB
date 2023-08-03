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

        parent = self.AUA

        vbox = VBoxContainer(position=Vector(0), size=Vector(300,200))
        self.AUA.viewport_size_changed.connect(vbox._sized)
        vbox.insert_under(parent)

        #
        hbox = HBoxContainer(position=Vector(0), size=Vector(300,200), border=[0,30,0,20])
        vbox.add_child(hbox, hbox.BFH_SCALEFIT | hbox.BFV_SCALEFIT)
        for i in range(3):
            item = RectItem()
            item.prop["color"] = Vector(0.7, 0, 0.7)
            hbox.add_child(item, item.BFH_SCALEFIT | item.BFV_SCALEFIT)


        item = RectItem()
        item.prop["color"] = Vector(1,1,0)
        vbox.add_child(item, item.BFH_SCALE | item.BFH_RIGHT | item.BFV_BOTTOM, Vector(120, 280))

        item = RectItem()
        item.prop["color"] = Vector(0.7)
        vbox.add_child(item, item.BFH_SCALEFIT, Vector(120, 60))

        self.AUA.set_min_size(vbox._get_minsize())    

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