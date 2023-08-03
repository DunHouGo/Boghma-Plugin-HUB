# !!注意!!
\_update()本质上是在DrawMsg() 函数中调用的, 所以注意避免直接调用 userarea 的 LayoutChanged() 方法 , 否则可能会因陷入死循环而导致的C4D崩溃

---
# GeUserArea

由于ualib库是基于GeUserArea模块进行封装产生的，为了更好的理解库内部的各种逻辑设计，我们有必要先简单了解一下 GeUserArea 在c4d中是怎么运作的。
![[c4d GeUserArea]]


---
# ualib是如何起到作用的？

![[Pasted image 20230320182948.png]]
ualib 主要是由 core模块和 utils模块组成， AdvanceUserArea（后简称AUA）是用户可以直接实例化使用的类，GeUserArea（后简称 ua）是AUA类的一个属性 (.ua)。
ua对象有一个.root 参数用于指定Node类型的根节点（默认是一个Node2D节点） ，Node对象继承自 BaseHierarchy 类所以可以设置父子节点关系，所有的事件和绘制都会通过Node对象进行向下传递。
当发生输入事件时，ua 的 InputEvent 方法会通过 msg 参数创建一个 BaseEvent 对象 ，调用 root 对象的 \_event(BaseEvent)方法 并将BaseEvent持续向下传递。
当调用绘制时，ua 的 DrawMsg 方法会调用 root 对象的 \_draw_event(ua), 并将ua对象向下传递。


