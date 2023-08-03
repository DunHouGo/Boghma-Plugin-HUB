# 快速使用

## AdvanceUserArea
#AdvanceUserArea
首先需要初始化 AdvanceUserArea类 。
```python

""" 
推荐插件看 "..\test\test_jack_000_basic creat.py"里面列举了所有基础Item的添加
"""
import c4d
import os
import sys
import importlib

import ualib
from ualib.core import *
#######################################  上方都是导入模块

class G4D_Test_MainDlg(c4d.gui.GeDialog):

    ID_GROUP_NONE = 1000
    ID_UA = 2000

    def __init__(self):
	    # 初始化一个 AdvanceUserArea 对象， GeUserArea是此对象的一个属性 .ua， 
        self.AUA = AdvanceUserArea()
        # 创建一个矩形对象 设置位置和大小
        item = RectItem(position=Vector(10), size=Vector(300,200))
        # 将 moveable 属性改为 True 可以让我们拖拽此对象
        item.prop["moveable"] = True
        # 将当前对象插入为 根对象的子级
        item.insert_under(self.AUA)



    def CreateLayout(self):
        self.SetTitle("ualib TEST")
        if self.GroupBegin(self.ID_GROUP_NONE, c4d.BFH_SCALEFIT| c4d.BFV_SCALEFIT, cols=1, rows=0, title="", groupflags=0, initw=0, inith=0):
            self.GroupBorderSpace(10, 5, 10, 10)
            # 标准的 GeUserArea 添加方法， 先添加区域
            self.AddUserArea(self.ID_UA, c4d.BFH_SCALEFIT| c4d.BFV_SCALEFIT, initw=0, inith=0)
            # 再指定该区域内要绘制的 GeUserArea 对象， 在这里就是 self.AUA.ua
            self.AttachUserArea( self.AUA.ua, self.ID_UA)
		    
        self.GroupEnd()
        return True

if __name__ == '__main__':
    dialog = G4D_Test_MainDlg()
    dialog.Open(c4d.DLG_TYPE_ASYNC, pluginid=0, xpos=-2, ypos=-2, defaultw=800, defaulth=800, subid=0)
```

运行脚本我们就应该可以看到屏幕窗口中出现了一个矩形框，并且我们可以拖动它。
所有其他对象的添加都是类似的形式。