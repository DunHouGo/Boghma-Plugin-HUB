import c4d
import os
import sys
import math
import importlib
import tokenize

SCRIPTPATH = os.path.dirname(__file__)
Lib_Path = os.path.dirname(os.path.dirname(SCRIPTPATH))

if Lib_Path not in sys.path:
    sys.path.append(Lib_Path)

import ualib
importlib.reload(ualib)
from ualib.core import *

BG_COLOR = Vector(0.1)

class TextEditor:

    def __init__(self, content):
        self._content = content
        self._cursor_position = None
        self._cursor_end_position = -1

    def __str__(self):
        return self._content
        
    def insert_text(self, start:int, text: str) -> None:
        if start is None or start < 0 or start > len(self._content):
            return
        self._content = self._content[:start] + text + self._content[start:]
        return start +len(text)

    def delete_text(self, start: int, end: int) -> None:
        if start is None or end is None or start < 0 or end > len(self._content) or start >= end:
            return
        deleted_text = self._content[start:end]
        self._content = self._content[:start] + self._content[end:]
        return start

    def move_cursor(self, position: int) -> None:
        if position is None or position < 0 or position > len(self._content):
            return
        self._cursor_position = position
    
    def get_cursor(self):
        return self._cursor_position

    def get_cursor_ln_col(self):
        cursour = self.get_cursor()
        if cursour is None:
            return None, None
        new_lines = self.get_lines()
        total_index = 0
        for ln, line_text in enumerate(new_lines):
            num = len(line_text)
            if cursour <= total_index+num:
                #print(_line, cursour, cursour-total_index)
                break
            total_index += num+1
        col = cursour-total_index
        
        return ln, col

    def move_cursor_by(self, key):
        if self._cursor_position is None:
            return 
        if key == 0 : # up
            cursor = self.get_cursor()
            ln, col = self.get_cursor_ln_col()
            if ln == 0:
                self.move_cursor(0)
                return
            up_line = len(self.get_line(ln-1))
            move_col = col
            if col > up_line:
                move_col = up_line
            self.move_cursor(cursor-col-up_line-1+ move_col)
        elif key == 1 : # down
            cursor = self.get_cursor()
            ln, col = self.get_cursor_ln_col()
            if ln >= len(self.get_lines())-1:
                self.move_cursor(len(self._content))
                return
            cur_line = len(self.get_line(ln))
            down_line = len(self.get_line(ln+1))
            move_col = col
            if col > down_line:
                move_col = down_line
            self.move_cursor(cursor-col+cur_line+1+move_col)
        elif key == 2 : # left
            cursor = self.get_cursor()
            self.move_cursor(cursor-1)
        elif key == 3 : # right
            
            cursor = self.get_cursor()
            self.move_cursor(cursor+1)

    def get_line(self, index):
        lines = self.get_lines()
        if 0 <= index and index < len(lines):
            return lines[index]
    
    def get_lines(self):
        return self._content.split("\n")

    

class MulityTextEditor(ClipMapTextItem):

    def __init__(self, content="", font_size=24):
        super().__init__(content, font_size) 
        self.TE = TextEditor(content)

        self.prop["clip_to_frame"] = True
        self.prop["color_text_bg"] = BG_COLOR
        self.scroll_w = 0
        self.scroll_h = 0
        self.line_hight = 0
        self.line_offset = 0
        self.skip_index = 0

        self.cursor = None
    
    def _wheel_event(self, event: BaseEvent):
        self.scroll_h += event.get_wheel_value()  # /20.0
        self.scroll_h = min(0, self.scroll_h)
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)
        event.set_handled()
        event.set_redraw()
    
    def _mouse_press_event(self, event: BaseEvent):

        if event.is_mouse_left_pressed():
            x, y = event.get_mouse_pos()
            self.set_cursor_position(x, y)
            self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)
            event.set_handled()
            event.set_redraw()

    def _key_press_event(self, event):
        
        if event.is_special_key_pressed(c4d.KEY_BACKSPACE):
            start = self.TE.get_cursor()
            cursurpos = self.TE.delete_text(start-1, start)
            self.TE.move_cursor(cursurpos)
        elif event.is_special_key_pressed(c4d.KEY_DELETE):
            start = self.TE.get_cursor()
            cursurpos = self.TE.delete_text(start, start+1)
            self.TE.move_cursor(cursurpos)

        elif event.is_special_key_pressed(c4d.KEY_ENTER):
            start = self.TE.get_cursor()
            cursurpos = self.TE.insert_text(start, "\n")
            self.TE.move_cursor(cursurpos)

        elif event.is_special_key_pressed(c4d.KEY_UP):
            self.TE.move_cursor_by(0)
        elif event.is_special_key_pressed(c4d.KEY_DOWN):
            self.TE.move_cursor_by(1)
        elif event.is_special_key_pressed(c4d.KEY_LEFT):
            self.TE.move_cursor_by(2)
        elif event.is_special_key_pressed(c4d.KEY_RIGHT):
            self.TE.move_cursor_by(3)
            
        else:
            value = event.get_key_value()
            start = self.TE.get_cursor()
            cursurpos = self.TE.insert_text(start, value)
            self.TE.move_cursor(cursurpos)

        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)
        event.set_handled()
        event.set_redraw()
      
    def get_text_size(self, text):
        cm = self.cm
        cm.BeginDraw()
        bc = c4d.bitmaps.GeClipMap.GetDefaultFont(c4d.GE_FONT_DEFAULT_SYSTEM)
        cm.SetFont(bc, self.prop["font_size"])
        tw = cm.TextWidth(text)
        cm.EndDraw()
        return tw

    def set_cursor_position(self, x, y):
        line_index = self.skip_index+ (y+self.line_hight+self.line_offset)//self.line_hight -1
        new_lines = self.TE.get_lines()
        line = new_lines[line_index]
        total_index = 0
        for _index, _line in enumerate(new_lines):
            if _index == line_index:
                break

            total_index += len(_line)+1

        cm = self.cm
        cm.BeginDraw()
        bc = c4d.bitmaps.GeClipMap.GetDefaultFont(c4d.GE_FONT_DEFAULT_SYSTEM)
        cm.SetFont(bc, self.prop["font_size"])

        end_x = 0
        over_half = True
        text = ""

        text_index = len(line)
        for text_index, text in enumerate(line):
            tw = cm.TextWidth(text)
            if text == " ":
                add_w = 2*tw
            else:
                add_w = tw
            end_x += add_w
            if x < end_x:
                over_half = (end_x-x) < add_w*0.5
                break

        cm.EndDraw()

        total_index += text_index
        if len(line) and over_half:
            total_index += 1
        self.TE.move_cursor(total_index)
        
    def _bake_text(self):
        w, h = int(self.size[0]), int(self.size[1])
        cm = self.cm
        
        # draw
        cm.Init(w, h, bits=32)
        cm.BeginDraw()
        bc = c4d.bitmaps.GeClipMap.GetDefaultFont(c4d.GE_FONT_DEFAULT_SYSTEM)
        cm.SetFont(bc, self.prop["font_size"])
        text_h = cm.TextHeight()
        self.line_hight = text_h
        # bg
        self.set_color(self.prop["color_text_bg"])
        cm.FillRect(0, 0, w, h)

        ln, col = self.TE.get_cursor_ln_col()
        
        # text
        self.set_color(self.prop["color"])
        # 跳过无需绘制的行
        start_x, start_y = int(self.scroll_w), int(self.scroll_h)
        self.skip_index = int(abs(start_y)//text_h)
        start_y = int((self.scroll_h-0.1)%text_h-text_h)
        self.line_offset = abs(start_y)
        new_lines = self.TE.get_lines()[self.skip_index:]
        self.cursor = None
        for index, line_text in enumerate(new_lines):
            if ln is not None and ln == self.skip_index+index:
                _front = line_text[:col].replace(" ", "  ")
                cursor_x = cm.TextWidth(_front)
                self.cursor = [cursor_x, start_y]
       
                
            line_text = line_text.replace(" ", "  ")
            w = max(w, cm.TextWidth(line_text))
            cm.TextAt(start_x, start_y, line_text)

            #cm.TextAt(start_x, start_y, str(self.skip_index+index))
            start_y+=text_h
            if start_y > self.size[1]:
                break

        cm.EndDraw()
        self._bmp = cm.GetBitmap().GetClone()
        
    def set_color(self, color):
        color *= 255
        self.cm.SetColor(int(color[0]), int(color[1]), int(color[2]), alpha=255)

    def _draw(self, ua):
        if not self._bmp:
            return 
        
        ua.DrawSetOpacity(self.prop["opacity"])
        w, h = int(self.size[0]), int(self.size[1])
        offset_x, offset_y = self.offset[0]*w, self.offset[1]*h
        pos = self.get_global_position()
        ua.DrawBitmap(self._bmp, int(pos[0]-offset_x), int(pos[1]-offset_y), w, h, 0, 0, w=w, h=h, mode=c4d.BMP_ALLOWALPHA)

        if self.cursor:
            ua.DrawSetPen(Vector(1))
            x1, y1 = self.cursor
            ua.DrawRectangle(x1, y1, x1+2, y1+self.line_hight)

    def _on_size_changed(self, size):
        self.size = Vector(size[0], size[1])
        self.dirty_flag.set_flag(self.DIRTYFLAGS_CHANGES)

class TextEditorPRE1(AreaNode):

    def __init__(self):
        super().__init__()
        self.cm = c4d.bitmaps.GeClipMap()
        self.cm.Init(0, 0, bits=32)
        self.insert_text = {}
        self.hover_text = None
        self.line_h = 0
        self.insert_text_index = None

    def _event(self, event: BaseEvent):
        """ 实现了基本的拖拽
        """
        super()._event(event)
        if event.is_handled():
            return 

        if event.is_down() and event.is_mouse_left_pressed():

            x, y = event.get_mouse_pos()
            import math
            line = math.floor((y+self.line_h*0.5)/self.line_h)
            tokens_line = self.all_lines[line]

            if self.hover_text and not self.hover_text.is_point_inside(x, y):
                self.hover_text = None

            if not self.hover_text:
                self.hover_text = tokens_line[-1]
            if not self.hover_text:
                return 

            
            #print(self.hover_text.name)
            res = self.hover_text.get_current_text(x, y)
            self.insert_text_index = self.hover_text.get_current_text_index(x,y)
            if not res:
                self.insert_text = []
            else: 
                x1, y1, x2, y2 = res
                if abs(x2-x) < abs(x1-x):
                    x1 = x2
                    self.insert_text_index+=1
                self.insert_text = [int(x1),int(y1),int(x1+2),int(y2)]
                

            event.set_handled()
            event.set_redraw()

        if event.is_down() and event.is_keyboard_pressed():
            key = event["asc"]
            if event["value"] == 1 and key:
                
                if self.hover_text:
                    text = self.hover_text.prop["text"]
                    text = text[0:self.insert_text_index] + key+ text[self.insert_text_index:]
                    
                    self.hover_text.set_change(text=text)
                    print(key)
                    event.set_redraw()
                    event.set_handled()
                    event.skip_hold()


    def _draw(self, ua):
        ua.DrawSetPen(BG_COLOR)
        ua.DrawRectangle(*self.get_global_bbox())
        self.size = ua.win_size

    def _draw_child(self, ua, parent_region: list):
        super()._draw_child(ua, parent_region)
        if self.insert_text:
            ua.DrawSetPen(Vector(1,0,0))
            ua.DrawRectangle(*self.insert_text)
        return 
    
        
    def viewport_size_changed(self, size):
        self.size = Vector(size[0], size[1])

    def tokenize(self, file_path):
        line_tokens_list = []
        with open(file_path, 'rb') as f:
            tokens = tokenize.tokenize(f.readline)
            #return [token for token in tokens]
            line_tokens = []
            for token in tokens:
                line_tokens.append(token)
                if token.type in [tokenize.NEWLINE, tokenize.NL, tokenize.ENCODING]:
                    line_tokens_list.append(line_tokens)
                    line_tokens = []
                elif token.type == tokenize.STRING and '"""' in token.string:
                    # 多行注释拆开成多个token
                    line_tokens.pop()
                    sep_list = token.string.split("\r\n")
                    token_start = token.start
                    for index, sep in enumerate(sep_list):
                        temp_token = tokenize.TokenInfo(tokenize.STRING,
                                                        string=sep,
                                                        start=token_start,
                                                        end=(len(line_tokens),len(sep)),
                                                        line=sep+'\r\n'
                                                        )
                        token_start = (len(line_tokens),0)
                        line_tokens.append(temp_token)
                        if index +1 != len(sep_list):
                            line_tokens.append(tokenize.TokenInfo(tokenize.NEWLINE,"",(0,0),(0,0),""))
                            line_tokens_list.append(line_tokens)
                            line_tokens = []
                    
                
        return line_tokens_list

    def convert(self, path):
        self.remove_all_children()
        line_token_list = self.tokenize(path)

        font_size=24
        start_x = 20
        start_y = 20
        cm = self.cm
        cm.BeginDraw()
        bc = c4d.bitmaps.GeClipMap.GetDefaultFont(c4d.GE_FONT_DEFAULT_SYSTEM)
        cm.SetFont(bc, font_size)

        space = "  "
        space_w = cm.TextWidth(space)
        x = start_x
        y = start_y
        w = 0
        h = self.cm.TextHeight()
        line_gap = h*0.2
        self.line_h = h + line_gap

        self.all_lines = []
        ln = 7 
        for line_number, line_tokens in enumerate(line_token_list):
            texts_line = []
            # if line_number < ln:
            #     continue
            # elif line_number > ln:
            #     break
            x = start_x
            for token_index, token in enumerate(line_tokens):
                #print(token_index, token)
                type = token.type
                text = token.string
                start = token.start[1]  # 列开始
                end = token.end[1]      # 列结束  
                w = cm.TextWidth(text)

                # pre process
                if type == tokenize.INDENT:
                    continue
                elif type == tokenize.DEDENT:
                    continue
                
                # creat_space
                if token_index == 0 :
                    space_start = 0
                elif line_tokens[token_index-1].type in [tokenize.INDENT, tokenize.DEDENT]:
                    space_start = 0
                else:
                    space_start = line_tokens[token_index-1].end[1]

                space_count = start-space_start
                if space_count:
                    space_text = space*space_count
                    item = self.add_new_item(space_text, x, y, font_size, -1, line_tokens)
                    texts_line.append(item)
                    x += space_w*space_count

                # add
                item = self.add_new_item(text, x, y, font_size, token_index, line_tokens)
                texts_line.append(item)

                # after process
                x += w
                if token.type in [tokenize.NEWLINE, tokenize.NL]:
                    x = 0
                    y += h+line_gap


            self.all_lines.append(texts_line)



        cm.EndDraw()
        return item.get_global_position()[1]+h*2
    
    def add_new_item(self, text, x, y, font_size, token_index, line_tokens): 
        parent = self
        item = TextLine(name=text, position=Vector(x, y))
        color = self.get_color(token_index, line_tokens)
        item.set_change(text=text, font_size=font_size, color= color )
        item.insert_under(parent)
        item.mouse_entered.connect(self._on_mouse_entered)
        item.mouse_exited.connect(self._on_mouse_exited)
        item.prop["redraw_on_mouse_entered"] = True
        item.prop["redraw_on_mouse_exited"] = True
        return item

    def _on_mouse_entered(self, node):
        node.color_ori = node.prop["color"]
        node.set_change(color=Vector(0.8,0.8,0))
        self.hover_text = node

    def _on_mouse_exited(self, node):
        node.set_change(color=node.color_ori)
        

    def get_color(self, index, tokens):
        python_keywords = [
             "False", "await", "else", "import", "pass", "None", "break", "except", "in", "raise", "True", "class", "finally", "is", "return", "and", "continue", "for", "lambda", "try", "as", "def", "from", "nonlocal", "while", "assert", "del", "global", "not", "with", "async", "elif", "if", "or", "yield"
         ]

        color = Vector(1)
        token = tokens[index]
        text = token.string
        if text in python_keywords:
            color = Vector(1,0.3,0.2)
        elif token.type == tokenize.OP:
            color = Vector(0.2,0.6,0.9)
        elif token.type == tokenize.NAME:
            if token.string[:2] == "__":
                color = Vector(0.2,0.6,0.9)
            elif tokens[index-1].string == "class":
                color = Vector(0.9,0.6,0.2)
            elif tokens[index+1].string == "(":
                color = Vector(0.9,0.6,0.8)
        elif token.type == tokenize.STRING:
            color = Vector(0.5,0.7,0.8)
        elif token.type == tokenize.NUMBER:
            color = Vector(0.5,0.5,0.8)
        elif token.type == tokenize.COMMENT:
            color = Vector(0.4)
        return color 
    
class TextLinePRE1(ClipMapTextItem):

    def __init__(self, name="", position=Vector(10,10), size=Vector(50, 50)):
        super().__init__()
        self.name = name
        self.position = position
        self.size = size
        self.prop["color_text_bg"] = BG_COLOR
        self.ms = None
        self.show_space = False

    
    def __repr__(self) -> str:
        return self.name

    def _event(self, event: BaseEvent):
        """ 实现了基本的拖拽
        """
        super()._event(event)
        if event.is_handled():
            return 
        
        if event.is_timer() and self.mouse_inside:
            x, y = event.get_mouse_pos()
            #self.get_current_text( x, y)
            #event.set_redraw()

    def get_current_text(self, x, y):
        pos = self.get_global_position()
        local = x-pos[0]
        if local<0:
            return 
        start = 0
        index = 0
        for index, w in enumerate(self.text_width_list):
            if start<=local and local<=start+w:
                break
            start += w
        
        self.ms = [int(pos[0]+start), int(pos[1]), int(pos[0]+start+w), int(pos[1]+self.size[1])]
        return [int(pos[0]+start), int(pos[1]), int(pos[0]+start+w), int(pos[1]+self.size[1])]

    def get_current_text_index(self, x, y):
        pos = self.get_global_position()
        local = x-pos[0]
        if local<0:
            return 
        start = 0
        index = 0
        for index, w in enumerate(self.text_width_list):
            if start<=local and local<=start+w:
                break
            start += w
        return index

    def _draw(self, ua):
        super()._draw(ua)
        
        if self.prop["text"].isspace() and self.show_space:
            num = len(self.prop["text"])/2
            _x1, _y1, _x2, _y2 = self.get_global_bbox()
            space = (_x2-_x1)/num
            for i in range(int(num)):
                ua.DrawSetPen(Vector(1,0,0))
                x1 = int(_x1+i*space)
                y1 = int(_y1)
                x2 = int(_x1+(i+1)*space)
                y2 = int(_y2)
                ua.DrawFrame(x1, y1, x2, y2, lineWidth=1, lineStyle=c4d.LINESTYLE_NORMAL)

        if self.ms and 0:
            ua.DrawSetPen(Vector(1,0,0))
            x1, y1, x2, y2 = self.ms
            #ua.DrawRectangle(x1, y1, x2, y2)
            ua.DrawFrame(x1, y1, x2, y2, lineWidth=2, lineStyle=c4d.LINESTYLE_NORMAL)
            self.ms = None


class G4D_Test_MainDlg(c4d.gui.GeDialog):

    ID_GROUP_NONE = 1000
    ID_Group_Scroll = 1001

    def __init__(self):
        self.AUA = AdvanceUserArea()

        file_path = r"D:\boghma\boghma hub\libs\boghma\simple_treeview.py"
        # 使用 'with' 语句自动处理文件关闭
        with open(file_path, 'r', encoding='utf-8') as file:
            file_contents = file.read()

        TE = MulityTextEditor(file_contents)
        TE.size = Vector(600)
        TE.insert_under(self.AUA)
        self.AUA.viewport_size_changed.connect(TE._on_size_changed)
        #self.AUA.viewport_size_changed.connect(TE.viewport_size_changed)
        #self.AUA.ua.draw_debug_frames = 1

        #self.AUA.set_min_size(Vector(20, h))


    def CreateLayout(self):
        self.SetTitle("ualib TEST")
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