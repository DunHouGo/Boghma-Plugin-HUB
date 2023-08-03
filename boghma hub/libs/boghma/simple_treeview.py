# -*- coding: utf-8 -*-  
#gui_treeview
import c4d 


def treeview_data():
    #创建tree view 相关的属性 treeview_data
    tv_Container = c4d.BaseContainer()
    #Border type
    tv_Container.SetLong(c4d.TREEVIEW_BORDER, c4d.BORDER_NONE) 
    #True if an object may be dropped under all the objects in the tree view.
    tv_Container.SetBool(c4d.TREEVIEW_OUTSIDE_DROP, False)  
    #True if no lines should be drawn.
    tv_Container.SetBool(c4d.TREEVIEW_HIDE_LINES, False) 
    #True if item may be duplicated by Ctrl + Drag.
    tv_Container.SetBool(c4d.TREEVIEW_CTRL_DRAG, False) 
    #True if no multiple selection is allowed.
    tv_Container.SetBool(c4d.TREEVIEW_NO_MULTISELECT, True) 
    #True if the tree view may have a header line.
    tv_Container.SetBool(c4d.TREEVIEW_HAS_HEADER, True) 
    #True if the column width can be changed by the user.
    #如果改成True 可以通过鼠标拖动的方式来修改columns的宽度
    tv_Container.SetBool(c4d.TREEVIEW_RESIZE_HEADER, True) 
    #True if the user can move the columns.
    #如果改成True 可以通过鼠标拖动的方式来修改columns的前后顺序
    tv_Container.SetBool(c4d.TREEVIEW_MOVE_COLUMN, False)
    #True if all lines have the same height.
    tv_Container.SetBool(c4d.TREEVIEW_FIXED_LAYOUT, True)
    #True if only the first line is asked for the columns width, resulting in a huge speedup.
    tv_Container.SetBool(c4d.TREEVIEW_NOAUTOCOLUMNS, True) 
    #True if it is not allowed to open the complete tree with Ctrl + Click.
    tv_Container.SetBool(c4d.TREEVIEW_NO_OPEN_CTRLCLK, True) 
    #True if Alt should be used instead of Ctrl for drag and drop; implies item may be duplicated by Alt + Drag.
    tv_Container.SetBool(c4d.TREEVIEW_ALT_DRAG, False) 
    #Disable “delete pressed” messages if backspace was hit.
    tv_Container.SetBool(c4d.TREEVIEW_NO_BACK_DELETE, True) 
    #Disable Delete Message Callback completely for backspace and delete.
    tv_Container.SetBool(c4d.TREEVIEW_NO_DELETE, True)
    #Alternate background per line.
    tv_Container.SetBool(c4d.TREEVIEW_ALTERNATE_BG, True) 
    #True if cursor keys should be processed. 
    # Note: The focus item has to be set to None if it is deleted and this flag is set.
    tv_Container.SetBool(c4d.TREEVIEW_CURSORKEYS,  False) 
    #Suppresses the rename popup when the user presses enter.
    tv_Container.SetBool(c4d.TREEVIEW_NOENTERRENAME, True) 
    #True to disable vertical scrolling and show the full list.
    tv_Container.SetBool(c4d.TREEVIEW_NO_VERTICALSCROLL, False) 
    #Show an add new column row at the bottom of the list.
    tv_Container.SetBool(c4d.TREEVIEW_ADDROW, False) 
    #The treeview is resizable from the bottom edge.
    tv_Container.SetBool(c4d.TREEVIEW_RESIZABLE, False) 
    return tv_Container

class BaseHierarchy():

    def __init__(self):
        self._parent = None 
        self._children = [] 

    #Hierarchy Navigation Methods
    def get_children(self):
        return self._children

    def get_down(self):
        if self._children:
            return self._children[0]

    def get_downlast(self):
        if self._children:
            return self._children[-1]

    def get_next(self):
        if self._parent and self._parent._children:
            index = self._parent._children.index(self)
            if index+1 != len(self._parent._children):
                return self._parent._children[index+1]

    def get_pred(self):
        if self._parent and self._parent._children:
            index = self._parent._children.index(self)
            if index != 0:
                return self._parent._children[index-1]

    def get_up(self):
        return self._parent

    #Insertion Methods
    def insert_after(self, obj):
        if obj and obj._parent and obj != self:
            index = obj._parent._children.index(obj)
            obj._parent._children.insert(index+1, self)
            self._parent = obj._parent
            return True
        else:
            return False

    def insert_before(self, obj):
        if obj and obj._parent and obj != self:
            index = obj._parent._children.index(obj)
            obj._parent._children.insert(index, self)
            self._parent = obj._parent
            return True
        else:
            return False
    def insert_under(self, obj):
        if obj and obj != self:
            obj._children.insert(0, self)
            self._parent = obj
            return True
        else:
            return False
    def insert_underlast(self, obj):
        if obj and obj != self:
            obj._children.append(self)
            self._parent = obj
            return True
        else:
            return False

    #advance
    def iter_all_children(self):
        for objx in self._children:
            yield objx
            for objx2 in objx.iter_all_children():
                yield objx2
    
    def remove(self):
        parent = self.get_up()
        if parent:
            self._parent = None 
            parent.get_children().remove(self)
            return True

        return False

    def remove_all_children(self):
        for obj in reversed(self._children):
            obj.remove()

class TreeViewBaseObject(BaseHierarchy):
    def __init__(self, id):
        super().__init__()
        
        self.id = id
        self.part = []
        self.userdata = {}
    
    def add_part(self, text, icon=None):
        self.part.append([str(text), icon])

    def get_part(self, index):
        if 0 <= index and index < len(self.part):
            return self.part[index]
    
    def change_part(self, index, text, icon=None):
        if 0 <= index and index < len(self.part):
            self.part[index] = [str(text), icon]
            return True

class TreeViewManager():

    ID_HEAD = 100

    def __init__(self, dlg, tvcg, head_list:list[str]=[]):       
        # tvcg = self.AddCustomGui(id=id, pluginid=c4d.CUSTOMGUI_TREEVIEW, name="", flags=c4d.BFH_SCALEFIT| c4d.BFV_SCALEFIT, minw=0, minh=0, customdata=treeview_data())
        self.dlg = dlg 
        self.tvcg = tvcg
        self.head_list = head_list

        self.select_list = []
        self.open_list = []

        self.prop = {}
        self.prop["normal_color"] = c4d.Vector(0.8)
        self.prop["select_color"] = c4d.Vector(0.9, 0.6, 0.3)
        self.prop["bgc_default"] = c4d.Vector(0.22) #默认单色背景
        self.prop["bgc_alternate"] = c4d.Vector(0.28)
        self.prop["bgc_select"] = c4d.Vector(0.1)
        self.prop["column_width"] = {"100":150}
        self.prop["use_drag"] = False
        self.prop["drag_insert_type"] = c4d.INSERT_BEFORE | c4d.INSERT_AFTER | c4d.INSERT_UNDER
        self.prop["empty_text"] = "TreeView is Empty"

        self.root = TreeViewBaseObject(id=-1)
        self.init_TreeViewCustomGui()

    def init_TreeViewCustomGui(self, treeview_function=None):
        layout_container = c4d.BaseContainer()
        if not treeview_function:
            treeview_function = TreeViewFunctions()
        for index, head_text in enumerate(self.head_list):
            if index == 0:
                ty = c4d.LV_USERTREE
            else:
                ty = c4d.LV_USER
            layout_container[self.ID_HEAD+index] = ty
             
        self.tvcg.SetLayout(len(self.head_list), layout_container)
        for index, head_text in enumerate(self.head_list):
            self.tvcg.SetHeaderText(self.ID_HEAD+index, head_text) 
        
        self.tvcg.SetRoot(root=self.root, functions=treeview_function, userdata=self)
        self.tvcg.Refresh()         
    
    def new_tvbo(self, id):
        return TreeViewBaseObject(id)
    #
    def select(self, obj_id, mode):
        if mode == c4d.SELECTION_ADD:
            if obj_id not in self.select_list:
                self.select_list.append(obj_id)
        elif mode == c4d.SELECTION_SUB:
            if obj_id in self.select_list:
                self.select_list.remove(obj_id)
        elif mode == c4d.SELECTION_NEW:
            self.select_list = [obj_id]
    
    def toggle_open(self, obj_id, opened):
        if opened and obj_id not in self.open_list :
            self.open_list.append(obj_id)
        elif obj_id in self.open_list : 
            self.open_list.remove(obj_id)

    #
    def get_by_id(self, id):
        for objx in self.root.iter_all_children():
            if objx.id == id:
                return objx

    def refresh(self):
        if self.tvcg:
            self.tvcg.Refresh()  
            return True

    def show_object(self, tvbo):
        self.tvcg.ShowObject(tvbo)
        self.tvcg.MakeVisible(tvbo)
    #
    def CreateContextMenu(self, obj, head) -> c4d.BaseContainer:
        pass
    
    def ContextMenuCall(self, obj, head, cid) -> None:
        pass
    
    def mouse_down(self, obj, head, mouseinfo, rightButton) -> None:
        pass
    
    def double_click(self, obj, head, mouseinfo) -> bool:
        pass
    
    def selection_change(self):
        pass
    #

class TreeViewFunctions(c4d.gui.TreeViewFunctions):

    #列表位置
    def GetFirst(self, root, userdata):
        return root.get_down()

    def GetDown(self, root, userdata, obj):
        return obj.get_down()

    def GetNext(self, root, userdata, obj):
        return obj.get_next()
         
    def GetPred(self, root, userdata, obj):
        return obj.get_pred()

    def GetBackgroundColor(self, root, userdata, obj, line, col):
        if obj.id in userdata.select_list:
            col = userdata.prop["bgc_select"]
        else:
            if line%2==0:
                col = userdata.prop["bgc_default"]
            else:
                col = userdata.prop["bgc_alternate"]
        return col
   
    def GetLineHeight(self, root, userdata, obj, col, area):
        return 20

    def GetHeaderColumnWidth(self, root, userdata, col, area):
        if str(col) in userdata.prop["column_width"]:
            return userdata.prop["column_width"][str(col)]
        else:
            return 40
    #Called to draw the cell for object obj in column col into the user area in drawinfo[‘frame’].
    def DrawCell(self, root, userdata, obj, col, drawinfo, bgColor):
        geUserArea = drawinfo["frame"]
        xpos = drawinfo["xpos"]
        ypos = drawinfo["ypos"] #
        default_height = drawinfo["height"]
        border = 2
        
        offsetX = 0
        #

        geUserArea.DrawSetPen(bgColor)
        geUserArea.DrawRectangle(xpos, ypos, xpos+2000, ypos+default_height)

        part = obj.get_part(col-userdata.ID_HEAD)
        if part:
            #icon
            text, icon = part
            if icon:
                #check icon
                if isinstance(icon, c4d.bitmaps.BaseBitmap):
                    draw_icon = icon
                elif isinstance(icon, list):
                    if obj.id in userdata.open_list :
                        draw_icon = icon[1]
                    else:
                        draw_icon = icon[0]

                geUserArea.DrawSetPen(bgColor)
                geUserArea.DrawRectangle(xpos, ypos, xpos+default_height, ypos+default_height)

                geUserArea.DrawBitmap(draw_icon,
                                    xpos+border, ypos+border, default_height -border*2, default_height -border*2, 
                                    0, 0, draw_icon.GetBw(), draw_icon.GetBh(), 
                                    c4d.BMP_ALLOWALPHA 
                                    )
                offsetX += default_height
                    
            #text
            if text:
                if obj.id in userdata.select_list:
                    text_color = userdata.prop["select_color"]
                else:
                    text_color = userdata.prop["normal_color"]
                
                geUserArea.DrawSetTextCol(text_color, bgColor)
                geUserArea.DrawText(text, offsetX +xpos +border, ypos+1)
        
    #Called to retrieve the selection status of object obj.
    def IsSelected(self, root, userdata, obj):
        if obj.id in userdata.select_list :
            return True
        else:
            return False
        
    #Called to select object obj.
    def Select(self, root, userdata, obj, mode):
        userdata.select(obj.id, mode)
        
    def IsOpened(self, root, userdata, obj):
        if obj.id in userdata.open_list:
            return True
        else:
            return False

    ##折叠 通过open来修改状态 通过isOpened来实行
    def Open(self, root, userdata, obj, opened):
        userdata.toggle_open(obj.id, opened)

    def CreateContextMenu(self, root, userdata, obj, lColumn, bc):
        #The added menu entry IDs must be larger than c4d.ID_TREEVIEW_FIRST_NEW_ID.
        #bc[c4d.FIRST_POPUP_ID+1] ="ContextMenu 1"
        bc.FlushAll()
        if not obj:
            obj = root
        if lColumn == -1:   
            head_text = userdata.head_list[-1]
        else:
            head_text = userdata.head_list[lColumn-userdata.ID_HEAD]
        bcMenu = userdata.CreateContextMenu(obj, head_text)
        if isinstance(bcMenu, c4d.BaseContainer) and len(bcMenu) != 0:
            bcMenu.CopyTo(bc, c4d.COPYFLAGS_NONE)
        
    def ContextMenuCall(self, root, userdata, obj, lColumn, lCommand):
        
        if not lCommand: #右键取消
            return False
        if not obj:
            obj = root
        if lColumn == -1:   
            head_text = userdata.head_list[-1]
        else:
            head_text = userdata.head_list[lColumn-userdata.ID_HEAD]
        userdata.ContextMenuCall(obj, head_text, lCommand)
        return False
    
    def MouseDown(self, root, userdata, obj, col, mouseinfo, rightButton):
        if col == -1:
            head_text = None
        else:
            head_text = userdata.head_list[col-userdata.ID_HEAD]
        userdata.mouse_down(obj, head_text, mouseinfo, rightButton)    
        if not obj and col == -1:
            userdata.select_list = []
            userdata.refresh()
            userdata.selection_change()

        return False    
    
    def DoubleClick(self, root, userdata, obj, col, mouseinfo):
        if col == -1:
            head_text = userdata.head_list[-1]
        else:
            head_text = userdata.head_list[col-userdata.ID_HEAD]
        userdata.double_click(obj, head_text, mouseinfo)   
        return True 

    def SelectionChanged(self, root, userdata):
        userdata.selection_change()    
            

    def GetDragType(self, root, userdata, obj):
        if not userdata.prop["use_drag"]:
            return c4d.NOTOK
        return c4d.DRAGTYPE_ATOMARRAY 

    def GenerateDragArray(self, root, userdata, obj):
        userdata.drag_obj = obj
        return [c4d.BaseObject(c4d.Onull)]

    def SetDragObject(self, root, userdata, obj):
        pass

    def DragStart(self, root, userdata, obj):
        return c4d.TREEVIEW_DRAGSTART_ALLOW | c4d.TREEVIEW_DRAGSTART_SELECT

    def AcceptDragObject(self, root, userdata, obj, dragtype, dragobject):
        return userdata.prop["drag_insert_type"] , False

    def InsertObject(self, root, userdata, obj, dragtype, dragobject, insertmode, bCopy):
        """
        Called when a drag is dropped on the TreeView.
        """
        if obj == userdata.drag_obj:
            return 
        for child in userdata.drag_obj.iter_all_children():
            if obj == child:
                return 
        userdata.drag_obj.remove()
        if insertmode == c4d.INSERT_AFTER:
            userdata.drag_obj.insert_after(obj)
        elif insertmode == c4d.INSERT_BEFORE:
            userdata.drag_obj.insert_before(obj)
        elif insertmode == c4d.INSERT_UNDER:
            userdata.drag_obj.insert_under(obj)
        return
    
    def EmptyText(self, root, userdata):
        return userdata.prop["empty_text"]