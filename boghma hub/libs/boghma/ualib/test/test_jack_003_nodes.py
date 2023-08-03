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


class NodeItem(RoundRectItem):

    def __init__(self, position=Vector()):
        super().__init__(position)
        w = 60
        h = 20
        self.size = Vector(w, h)*2
        self.prop["moveable"] = True
        self.prop["fill"] = True
        self.prop["clip_children"] = False

        s1 = SlotItem(position=Vector(0,h))
        s1.insert_under(self)
        s2 = SlotItem(position=Vector(w*2,h))
        s2.insert_under(self)
        self.input = s1
        self.output = s2


        text = SimpelTextItem(text="BaseNode", position=Vector(w,h))
        text.offset = self.ALIGNMENT_CENTER
        text.insert_under(self)

        self.extend_shapes([s1, s2])

    def get_slot(self, x, y):
        for slot in [self.input, self.output]:
            if slot.is_point_inside(x, y):
                return True




class SlotItem(RoundRectItem):

    def __init__(self, position=Vector()):
        super().__init__(position=position, size=Vector(16))
        self.prop["color"] = Vector(0.8)
        self.prop["raidus"] = 8

        self.offset = self.ALIGNMENT_CENTER

    def _mouse_enter_event(self, event: BaseEvent):
        """
        鼠标进入事件在这里执行
        """
        self.change_size(Vector(24))
        event.set_redraw()

    def _mouse_leave_event(self, event: BaseEvent):
        """
        鼠标离开事件在这里执行
        """
        self.change_size(Vector(16))
        event.set_redraw()





class LinkItem(BaseBezierItem):

    def __init__(self, position=Vector(), size=Vector()):
        super().__init__()
        self.prop["color"] = Vector(0.8)
        self.state = 0

    def single_connect(self, node):
        self.state = 1
        start_pos = node.output.get_global_position()
        self.add_bezier_object(start=start_pos, end=start_pos ,start_hand_offset=Vector(50,0), end_hand_offset=Vector(-50,0), update=True)


    def connect(self, output_node, input_node):
        self.state = 2
        self.output_node = output_node
        self.input_node = input_node
        self.output_node.global_frame_changed.connect(self.update_position)
        self.input_node.global_frame_changed.connect(self.update_position)
        self.update_position()


    def update_position(self):
        start_pos = self.output_node.output.get_global_position()
        end_pos = self.input_node.input.get_global_position()
        self.change_object(0, "start", start_pos, update=False)
        self.change_object(0, "end", end_pos, update=True)



class Scene(Node2D):


    def __init__(self,aua):
        super().__init__()
        self.aua = aua
        self.insert_under(aua)

        self.state = 0

        self.inside_nods = []
        self.nodeconnect = []
        self.current_line = None

        #line = LinkItem()
        #line.insert_underlast(self)
        #line.connect(node, node2)

    def new_node(self, pos):
        node = NodeItem(pos)
        node.insert_under(self)
        node.mouse_entered.connect(self._on_mouse_entered)
        node.mouse_leave.connect(self._on_mouse_leave)

    
    def _mouse_move_event(self, event: BaseEvent):
        super()._mouse_move_event(event)
        if event.is_handled():
            return
        if self.current_line and self.current_line.state == 1:
            x, y = event.get_mouse_pos()
            self.current_line.change_object(0, "end", Vector(x,y), update=True)
            event.set_redraw()

    def _mouse_press_event(self, event: BaseEvent):
        super()._mouse_press_event(event)
        if event.is_handled():
            return
        
        x, y = event.get_mouse_pos()
        if event.is_mouse_right_pressed():
            self.new_node(Vector(x,y)-Vector(60,20))
            event.set_redraw()
            event.set_handled()
            return

        if self.inside_nods:
            node = self.inside_nods[0]
            if node.get_slot(x,y):
                if self.state == 0:
                    self.state = 1
                    self.nodeconnect = [node]
                    line = LinkItem()
                    line.insert_underlast(self)
                    line.single_connect(node)
                    self.current_line = line

                elif self.state == 1:
                    self.state = 0
                    self.nodeconnect.append(node)
                    self.current_line.connect(self.nodeconnect[0], self.nodeconnect[1])
                    self.current_line.update_position()
                    self.current_line = None
                    event.set_redraw()
                    event.set_handled()
        else:
            if self.state == 1:
                self.state = 0
                if self.current_line:
                    self.current_line.remove()
                    self.current_line = None
                    event.set_redraw()


    def _on_mouse_entered(self, node):
        if node not in self.inside_nods:
            self.inside_nods.append(node)

    def _on_mouse_leave(self, node):
        if node in self.inside_nods:
            self.inside_nods.remove(node)

class G4D_Test_MainDlg(c4d.gui.GeDialog):

    ID_GROUP_NONE = 1000

    def __init__(self):
        self.AUA = AdvanceUserArea()
        self.AUA.ua.draw_debug_frames = 0

        self.scene = Scene(self.AUA)

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