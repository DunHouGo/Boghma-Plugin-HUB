#GeUserArea

GeUserArea 是C4D中的绘制模块。
官方SDK https://developers.maxon.net/docs/Cinema4DPythonSDK/html/modules/c4d.gui/GeUserArea/index.html
基础使用方式 https://community.boghma.com/d/45

在 core 模块中内置了 同名的 GeUserArea 类，用于在c4d中接受事件 绘制图形，用户除了在GeDialog中添加 ua时外（具体代码参考 #AdvanceUserArea ), 几乎无需访问或者修改 GeUserArea对象。
==这也是ualib存在的意义，通过封装和添加功能让原先比较底层的 GeUserArea 变得更加直观和好用。==

----
# 重要概念

## 覆写函数
GeUserArea 模块中比较常用的几个覆写函数： 
```python
# 比较常用的
InputEvent()  在 ua 区域发生事件时自动调用，如点击 双击 滚轮等，返回为True 处理当前事件， 返回为False时会忽略当前事件
Timer() 通过 self.SetTimer(millsec) 函数设置一次即可，0为停止， 否则会根据设置的毫秒固定周期调用一次 Timer 函数， 默认为0
DrawMsg() 所有的绘制都会发生在这里，可以通过两种方式调用绘制 self.Redraw() （小更新） 或者 self.LayoutChanged() （大更新）

# ---下面就是一些不那么常用的函数
Init()  当dialog界面创建时会默认调用一次 方法（不是初始化 __init__ 方法, 所以几乎用不到）
GetMinSize()  返回ua区域的最小尺寸 这个用于 限制dialog中的控件尺寸（比如设置了最小尺寸 scroll group才会起效果），需要通过 self.LayoutChanged() 调用
Sized()  当ua区域发生变化时自动调用 也可以通过self.LayoutChanged()调用
InitValues() 绘制前的更新 需要通过 self.LayoutChanged()调用

```

这里需要着重说一下： self.LayoutChanged() 
默认使用 self.Redraw() 足以起到刷新绘制的作用 ，但是当界面尺寸相关的属性发生改变时一定要调用 self.LayoutChanged() 来刷新画布。
self.LayoutChanged() 默认会按顺序激活以下四个步骤：
```Python
GetMinSize() # 获取最小尺寸
Sized()  # 尺寸修改
InitValues()  # 更新
DrawMsg()  # 绘制
```
另外，在 DrawMsg() 里一定要记得调用 self.OffScreenOn() 
```python
def DrawMsg(self, x1, y1, x2, y2, msg):
	self.view = [x1, y1, x2, y2]
	self.OffScreenOn() # Double buffering
	#...绘制事件写在这里
```

## c4d Message
还有一个比较重要的就是 Message()
Message是 c4d内部模块间通讯的机制，你可以理解为所有c4d 对象都会有这个 Message方法用于传递数据和信息，
GeUserArea 中的 Message函数可以帮助我们接受C4D中正在发生的一些信息，并对此作出相应的反馈。

比如我们经常会在鼠标进入 GeUserArea 区域时调用 Timer函数，就会这么写：
```python
def Message(self, msg, result):
	if msg.GetId() == c4d.BFM_GETCURSORINFO: # 当鼠标进入 ua区域时触发
		if not self.timer_state:
			self.timer_state = True
			self.SetTimer(30)  # 开启Timer 30毫秒一次
			return True
			
	return c4d.gui.GeUserArea.Message(self, msg, result)
```

因为当鼠标离开区域时 c4d不会通过message通知我们( c4d.BFM_CURSORINFO_REMOVE 虽然有这个message，但是不知道为啥接收不到), 所以我们需要自己在 Timer函数里做鼠标退出事件的判定并关闭 Timer（如果有必要的话）。
```python

def DrawMsg(self, x1, y1, x2, y2, msg):
    self.view = [x1, y1, x2, y2] # 获取界面范围
    ...
    
def Timer(self, msg):
	x, y = self._GetMousePos(msg) # 获取鼠标位置
	x1, y1, x2, y2 = self.view  # 这个参数可以在 DrawMsg时保存下来
	if (x < x1 or y < y1 or x >= x2 or y >= y2) and self.timer_state:
		self.timer_state = False  # 当鼠标超出画布时返回 False
	if not self.timer_state:
		self.SetTimer(0)  # 停止Timer
		
	# timer相关的事件可以写在这里
		
def _GetMousePos(self, msg): 
	# 获取鼠标位置
	msg = c4d.BaseContainer(msg)
	self.GetInputState(c4d.BFM_INPUT_MOUSE, c4d.BFM_INPUT_MOUSELEFT, msg)
	x, y = msg.GetInt32(c4d.BFM_INPUT_X), msg.GetInt32(c4d.BFM_INPUT_Y)
	map_ = self.Global2Local()
	x += map_['x']
	y += map_['y']
	return x, y

```

