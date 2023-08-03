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

    def __init__(self):
        self.AUA = ualib.base.AdvanceUserArea()

    def CreateLayout(self):
        self.SetTitle("g4d TEST")

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
