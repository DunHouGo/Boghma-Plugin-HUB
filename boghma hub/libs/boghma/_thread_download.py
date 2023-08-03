import c4d
import os
import requests
import math
import traceback
import time

from c4d import BaseContainer

class Signal:
    """用于模仿pyqt中的Signal类。"""

    def __init__(self, *args_types, **kwargs_types):
        self._slots = []
        # self._args_types = args_types
        # self._kwargs_types = kwargs_types

    def connect(self, slot):
        """将槽函数连接到信号上。"""
        if slot not in self._slots:
            self._slots.append(slot)

    def disconnect(self, slot):
        """将槽函数从信号上断开连接。"""
        if slot in self._slots:
            self._slots.remove(slot)

    def emit(self, *args, **kwargs):
        """发送信号，调用所有连接的槽函数。"""
        for slot in self._slots:
            slot(*args, **kwargs)

class ThreadFunction(c4d.threading.C4DThread):
    """万能的多线程包装方法"""
    def __init__(self, func=None, *args, **kwargs):
        self.successed = Signal()
        self.failured = Signal()
        if func:
            self.init_function(func, *args, **kwargs)

    def init_function(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def Main(self):
        try:
            self.successed.emit(self.func(*self.args, **self.kwargs))
        except:
            self.failured.emit(traceback.format_exc())

class DownloadHelper:

    def __init__(self, chunch_size=None):
        self.num_info_changed = Signal("downloaded_size", "total_size" ,"chunk", "progress")
        self.str_info_changed = Signal("downloaded_size", "total_size" ,"chunk", "progress")

        self._chunk_size = chunch_size if chunch_size else 1024*1024*2
    
    def set_chunk_size(self, chunk_size):
        self._chunk_size = chunk_size

    def stop_download(self):
        self._stoped = True

    def download(self, url, file_path):
        self._url = url
        self._file_path = file_path
        self._stoped = False
        response = requests.get(self._url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        with open(self._file_path, 'wb') as file:
            for data in response.iter_content(self._chunk_size):
                if self._stoped:
                    break
                chunk = len(data)
                downloaded_size += chunk
                file.write(data)
                progress = (downloaded_size / total_size) * 100
                self.num_info_changed.emit(downloaded_size, total_size, chunk, progress)
                self.str_info_changed.emit(self.convert_size(downloaded_size), self.convert_size(total_size), self.convert_size(chunk), "{:.2f}%".format(progress))
                
        if not self._stoped:
            return self._file_path
 
    @staticmethod
    def convert_size(size_bytes):
        if size_bytes <= 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = '%.1f' % (size_bytes / p)
        res = "%s %s" % (s, size_name[i])
        return res
    


PluginId = -1000

class Dialog(c4d.gui.GeDialog):
    """docstring for """
    ID_Group_None = 1000
    ID_Button = 2000
    ID_Static = 2001
    ID_Button_Stop = 2002
    def __init__(self):
        self._download_info = []
        
        self.download_helper = DownloadHelper(1) 
        self.download_helper.str_info_changed.connect(self._on_downloading)

        self.download_thread = ThreadFunction()
        self.download_thread.successed.connect(self._on_download_finished)
        self.download_thread.failured.connect(self._on_download_failured)

    def CreateLayout(self):
        self.SetTitle("test")
        if self.GroupBegin(self.ID_Group_None, c4d.BFH_SCALEFIT |c4d.BFV_SCALEFIT, 1, 0, ""):
            self.GroupBorderSpace(10,10,10,10)

            self.AddButton(self.ID_Button, c4d.BFH_SCALEFIT, name="Download")
            self.AddStaticText(self.ID_Static, c4d.BFH_SCALEFIT, name="Info:")
            self.AddButton(self.ID_Button_Stop, c4d.BFH_SCALEFIT, name="Stop")

        
        self.GroupEnd()
        return True

    def InitValues(self):
        return True

    def CoreMessage(self, id, msg) :
        if id==PluginId:
            self.SetString(self.ID_Static, self._download_info)
            self.LayoutChanged(self.ID_Group_None)
            return True
        return True

    def Command(self, id: int, msg: BaseContainer) -> bool:
        if id == self.ID_Button:
            self.download_from_thread(url="https://tm-image.tianyancha.com/tm/89a48e258daa4c2bdf44f839c52c77f7.jpg",
                                      file_path=r"C:\Users\Administrator\Desktop\新建文件夹\test.jpg")
        elif id == self.ID_Button_Stop:
            self.download_helper.stop_download()
        return True

    ##
    def _on_download_finished(self, result):
        # 这个函数本质上是在thread里被调用
        # 下载成功 result -> download file path
        print("下载结束！")
        if result:
            self.set_download_info(f"Info: {result}")
        else:
            self.set_download_info("Info: 下载中断")

                       
    def _on_download_failured(self, error_message):
        # 这个函数本质上是在thread里被调用
        # 下载失败
        print("下载失败！", error_message)

    def _on_downloading(self, progress, downloaded_size, total_size , chunk):
        # 这个函数本质上是在thread里被调用
        # 正在下载时
        self.set_download_info(f"Info: {progress}/ {downloaded_size}, {total_size} - {chunk}")
        time.sleep(1)

    def set_download_info(self, info):
        self._download_info = info
        c4d.SpecialEventAdd(PluginId)

    def download_from_thread(self, url, file_path):
        if self.download_thread.IsRunning():
            print("正在下载其他项目，等下载任务结束后重试" )
            return False
        self.download_thread.init_function(self.download_helper.download, url, file_path)
        self.download_thread.Start()





if __name__ == "__main__":
    dialog = Dialog()
    dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=0, defaulth=800, defaultw=800, xpos=- 2, ypos=- 2)