```
0. pip install sphinx
1. 将 sphinx 添加环境变量，方便后续在其他文件夹调用方法
2. 创建doc文件夹，打开cmd 输入：sphinx-quickstart
3. cmd 继续写入配置（一直下一步 直到结束）
4. 设置 config.py：重点添加以下几个
	
	extensions = ['sphinx.ext.autodoc',
	              'sphinx.ext.napoleon',  
	              'sphinx.ext.todo',
	              'sphinx.ext.coverage',
	              'sphinx.ext.intersphinx'
	              ]
	# 将模块路径添加到 sys.path 我在这里直接用了绝对路径
	import os, sys
	path = r"D:\boghma\boghma hub\libs"  # 文件夹下有个 boghma 模块
	sys.path.insert(0, path)
	
	html_theme = 'sphinx_rtd_theme'  # 这个主题比较好看
	html_static_path = ['_static']

5. doc文件夹里cmd 输入：sphinx-apidoc -o ./source 'D:\boghma\boghma hub\libs\boghma'  这一步会自动生成.rst文件
6. doc文件夹里 make html 
7. .\spnix_docs\build\html\index.html 查看
8. make clean 可以清空文档
```

http://doc.yonyoucloud.com/doc/zh-sphinx-doc/markup/para.html
```
.. image:: _static/ualib_structure.png

.. note::
.. code-block:: python
.. seealso:: modules :py:mod:`zipfile`, :py:mod:`tarfile`
.. hlist::
	:columns: 1
	
:param x1: The upper left x coordinate.
:type x1: int

:rtype: int
:return: The return value depends on the message.
```


```python
#文档注释
def xx():
	"""
	| Called when Cinema 4D wants you to draw your userarea.

	.. note::
	
            If overridden, include a call to the base version of this function, :meth:`GeUserArea.Message`:
    
            .. code-block:: python
    
                def Message(self, msg, result):
                    if msg.GetId():
                        #Do something
                        return True
    
                    return c4d.gui.GeUserArea.Message(self, msg, result)
    
        .. seealso::
    
            :doc:`/consts/MSG_C4DATOM_PLUGINS` for information on the messages type, data and input/output.
    
	:param x1: The upper left x coordinate.
	:type x1: int
	:rtype: int
    :return: The return value depends on the message.
	"""

```

效果参考如下图：
```python 

def DrawMsg(self, x1: int, y1: int, x2: int, y2: int, msg: BaseContainer) -> None:
        """
        | Called when Cinema 4D wants you to draw your userarea.
        | Use the drawing functions to update your user area in the region specified by the rectangle from (x1,y1) to (x2,y2).
    
        :type x1: int
        :param x1: The upper left x coordinate.
        :type y1: int
        :param y1:  The upper left y coordinate.
        :type x2: int
        :param x2: The lower right x coordinate.
        :type y2: int
        :param y2: The lower right y coordinate.
        :type msg: c4d.BaseContainer
        :param msg: A mesage container.
        """
        pass

```
![[Pasted image 20230321205404.png]]

```python

def Message(self, msg: BaseContainer, result: BaseContainer) -> int:
        """
        Override this function to react to more messages than covered by the other functions. Normally this is not necessary.
    
        .. note::
    
            If overridden, include a call to the base version of this function, :meth:`GeUserArea.Message`:
    
            .. code-block:: python
    
                def Message(self, msg, result):
                    if msg.GetId():
                        #Do something
                        return True
    
                    return c4d.gui.GeUserArea.Message(self, msg, result)
    
        .. seealso::
    
            :doc:`/consts/MSG_C4DATOM_PLUGINS` for information on the messages type, data and input/output.
    
        :type msg: c4d.BaseContainer
        :param msg: The message container.
        :type result: c4d.BaseContainer
        :param result: A container to store results in.
        :rtype: int
        :return: The return value depends on the message.
        """
        pass
```
![[Pasted image 20230321205628.png]]