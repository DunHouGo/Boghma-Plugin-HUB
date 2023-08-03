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


BMP = ualib.utils.get_bitmap_from(os.path.join(SCRIPTPATH,"sequnce","Image.png"))


class Spirte(Node2D):

    def __init__(self):
        super().__init__()
        self.position = Vector(400)
        self.size = Vector(200)
        self.prop["bitmap"] = BMP
        self.frame_area = [0, 0, 200, 200]
        self.offset = self.ALIGNMENT_CENTER
        self.pic_size = [200,200]
        self.col = 5

    def _mouse_move_event(self, event: BaseEvent):
        x, y = event.get_mouse_pos()
        mp = Vector(x, y)
        op = self.get_global_position()
        v1 = mp-op
        v1[2] = 0
        v2 = Vector(1,0)
        ag = c4d.utils.GetAngle(v1.GetNormalized(), v2)
        dg = c4d.utils.RadToDeg(ag)
        if mp[1] > op[1]:
            dg = 360-dg
        dg-=15
        if dg < 0:
            dg = 360-abs(dg)
        index = int((dg/360.0)*25)
        self.change_index(index)
        
        event.set_redraw()

    def change_index(self, index):
        col = index % self.col
        row = index // self.col
        self.frame_area = [self.pic_size[0]*col, self.pic_size[1]*row, self.pic_size[0], self.pic_size[1]]
    

    def _draw(self, ua):
        if not self.prop["bitmap"]:
            return 
        x1, y1, x2, y2 = self.get_global_bbox()
        ua.DrawBitmap(self.prop["bitmap"], x1, y1, x2-x1, y2-y1, 
                                           *self.frame_area,  
                                           mode=c4d.BMP_ALLOWALPHA )
        ua.DrawSetPen(Vector(1))
        #ua.DrawFrame(x1, y1, x2, y2, lineWidth=1, lineStyle=c4d.LINESTYLE_NORMAL)
        pos = self.get_global_position()
        pos = [int(pos[0]), int(pos[1])]
        #ua.DrawFrame(pos[0],pos[1], pos[0]+4,pos[1]+4, lineWidth=2, lineStyle=c4d.LINESTYLE_NORMAL)



class G4D_Test_MainDlg(c4d.gui.GeDialog):

    ID_GROUP_NONE = 1000

    def __init__(self):
        self.AUA = AdvanceUserArea()
        sprite = Spirte()
        sprite.insert_under(self.AUA)

    def CreateLayout(self):
        self.SetTitle("ualib TEST")

        if self.GroupBegin(self.ID_GROUP_NONE, c4d.BFH_SCALEFIT| c4d.BFV_SCALEFIT, cols=1, rows=0, title="", groupflags=0, initw=0, inith=0):
            self.GroupBorderSpace(10, 5, 10, 10)
            self.AddUserArea(100, c4d.BFH_SCALEFIT| c4d.BFV_SCALEFIT, initw=0, inith=0)
            self.AttachUserArea( self.AUA.ua, 100)    
            #self.AddButton(self.ID_BTN_TEST, c4d.BFH_SCALEFIT, name=self.symbol[self.ID_BTN_TEST])

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
