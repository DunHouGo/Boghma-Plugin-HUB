
信号系统 #signal 是 ualib库最重要的类之一(在 utils 模块中)， 他负责整个模块对象间的信息传递。

```python
# 实例化， 参数可以用来限制emit时传入参数的类型
signal = Signal(*args_types, **kwargs_types)
# 连接函数，可以连接多个
signal.connect(slot: Callable)
# 取消连接
signal.disconnect(slot: Callable)
# 发送信号， 本质上就是调用之前连接的所有函数
signal.emit(*args, **kwargs)
```


# signal的运作机制

```python

def foo():
	print("signal is emited")


# 1 首先创建一个 signal object
so = Signal()

# 2 将信号与任意函数相连
so.connect(foo)

# 3 在任意时机发送信号
so.emit()

# 4 与信号连接的所有函数都会因为信号发送而执行
>>> "signal is emited"


```



信号可以是一对一或者一对多, 执行顺序由连接顺序决定
```python

def foo():
	print("signal is emited")
	
def foo2():
	print("signal is emited 2")


so = Signal()
so.connect(foo)
so.connect(foo2)
so.emit()

>>> "signal is emited"
>>> "signal is emited 2"

```

可以用信号发送参数，但参数必须也要在连接函数中定义, 
```python

def foo(x):
	print(f"signal is emited:{x}")

so = Signal()
so.connect(foo)
so.emit("anything")  

>>> "signal is emited: anything"


```

```python

def foo(x, y):
	print(f"signal is emited:{x}, {y}")

so = Signal()
so.connect(foo)
so.emit("anything", "anything2")  

>>> "signal is emited: anything, anything2"

```

可以通过信号发送信号
```python

def foo(x):
	print(f"signal is emited:{x}")

so = Signal()
so2 = Signal()
so.connect(so2.emit)
so2.connect(foo)
so.emit("anything")  

# so -> so2 -> foo
>>> "signal is emited: anything"


```

在定义信号的时候传入对应的数据类型来限制参数。

```python

def foo(x):
	print(f"signal is emited:{x}")

so = Signal(str) # 规定这个 signal 发送信号的参数是 str 类型
so.connect(foo)
so.emit("anything")  

so.emit(319)  # 当你发送非 str 的信号参数, Signal 会报错


>>> "signal is emited: anything"
>>> TypeError: Expected argument 1 to be of type <class 'str'>, but got <class 'int'>

```

# 注意事项

当用类全局域添加Signal可能会造成不同实例对象复用同一个signal的情况（这是python的设计问题，有些情况可以利用这个特性，但是通常尽量避免直接在全局域创建）

### 可能会造成问题的用法
```python


class Foo:

    sig1 = Signal()  # 全局域
    
    def __init__(self):
        self.sig1.connect(self.foo)  # 这样使用会有子类继承重复添加信号函数的风险
        
    def foo(self):
        pass

# 因为 a1 和 a2 共用同一个 sig1 所以会有两个 slot, 这是不对的
a1 = Foo() 
a2 = Foo() 
print(len(a1.sig1._slots))  # >>> 2 
# 这里会发生的情况是：当我们调用a2对象sig1.emit 时，a1对象连接的函数也会被调用
# 这样的结构特殊需求下有可能有用 但这里不是我们想要的结果

```

### 正确用法 
```python


class Foo:
    def __init__(self):
	    sig1 = Signal()  # 这样就没问题
        self.sig1.connect(self.foo)  

	def foo(self):
	        pass

a1 = Foo() 
a2 = Foo() 
print(len(a1.sig1._slots))  # >>> 1

```
