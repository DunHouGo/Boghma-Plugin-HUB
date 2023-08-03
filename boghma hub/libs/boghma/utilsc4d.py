""" 
c4d 相关的命令可以写在这里
"""
import os
import c4d
import subprocess
import boghma.utils

## language
def GetDefaultLanguage():
    # {'extensions': 'en-US', 'name': 'English', 'default_language': True}
    index = 0
    while True:
        lang = c4d.GeGetLanguage(index)
        if lang is None:
            break
        if lang["default_language"]:
            return lang
        index += 1


## c4d threading
class ThreadFunction(c4d.threading.C4DThread):
    """万能的多线程包装方法"""
    
    def __init__(self):
        self.info = ""
    
    def is_running(self):
        return self.IsRunning()

    def start(self):
        self._end = False
        self.Start()

    def end(self):
        self._end = True
        self.End()

    def set_function(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = True
        
    def Main(self):
        self.result = self.func(*self.args, **self.kwargs)


## GUI
def alert(title, msg, head="[WARNING]"):
    newline = "\n"
    if len(title)+len(head)>=len(msg):
        newline = " "
    else:
        newline = "\n"
    e_text = f"{head} {title}:{newline}{msg}"
    if head == "[WARNING]":
        alert_type = c4d.GEMB_ICONEXCLAMATION
    elif head == "[QUESTION]":
        alert_type = c4d.GEMB_ICONQUESTION| c4d.GEMB_OKCANCEL
    elif head == "[DONE]":
        alert_type = c4d.GEMB_ICONASTERISK
    else:
        alert_type = c4d.GEMB_FORCEDIALOG
    return c4d.gui.MessageDialog(e_text, type=alert_type)


class GroupWightsObject:

    def __init__(self, dialog, Group_id, wigth_list=[]):
        self.dialog = dialog
        self.Group_id = Group_id
        self.groupWeights = c4d.BaseContainer()
        self.wigth_list = wigth_list
        #
        self.groupWeights_save = False

    def get_group_weights(self):
        wlist = []
        for i, j in enumerate(self.wigth_list):
            w = self.groupWeights.GetFloat(c4d.GROUPWEIGHTS_PERCENT_W_VAL +i)
            wlist.append(w)
        return wlist

    def set_group_weights(self):
        #这个属性控制不同模块中间的分割线位置
        """
        #! use in InitValues function of dialog
        """
        if not self.groupWeights_save:
            self.groupWeights = c4d.BaseContainer()
            self.groupWeights.SetInt32(c4d.GROUPWEIGHTS_PERCENT_W_CNT, len(self.wigth_list))     
            for i, j in enumerate(self.wigth_list):
                self.groupWeights.SetFloat(c4d.GROUPWEIGHTS_PERCENT_W_VAL  +i, j)
            self.groupWeights_save = True
        self.dialog.GroupWeightsLoad(self.Group_id, self.groupWeights)
        self.dialog.LayoutChanged(self.Group_id)
    
    def groupwight_change(self, msg):
        """
        #! use in Message function of dialog
        """
        if msg.GetId() == c4d.BFM_WEIGHTS_CHANGED:
            # Retrieves the dragged host group
            if msg.GetInt32(c4d.BFM_WEIGHTS_CHANGED) == self.Group_id:
                # Stores the new weights values
                self.groupWeights = self.dialog.GroupWeightsSave(self.Group_id)
                return True



## DOC
def clone_open_scene(c4dfile_path, new_name=""):
    assert os.path.exists(c4dfile_path), f"clone_open_scene fail: file ({c4dfile_path}) not exists."

    loadflags = c4d.SCENEFILTER_OBJECTS | c4d.SCENEFILTER_MATERIALS
    ori_doc= c4d.documents.LoadDocument(c4dfile_path, loadflags)
    texture_globalize(ori_doc)
    new_doc = ori_doc.GetClone(0)
    if not new_name:
        new_name = os.path.basename(c4dfile_path).split(".")[0]+"(clone)"
    new_doc.SetDocumentName(new_name)
    new_doc.SetDocumentPath("")
    c4d.documents.InsertBaseDocument(new_doc)
    c4d.documents.KillDocument(ori_doc)

    c4d.EventAdd()
    return new_doc



def save_project_with_asset(doc, file_path, flags=None):
    
    doc = doc.GetClone(0)
    c4d.documents.InsertBaseDocument(doc)
    flags = ( c4d.SAVEPROJECT_ASSETS
            | c4d.SAVEPROJECT_SCENEFILE
            | c4d.SAVEPROJECT_DONTFAILONMISSINGASSETS
            | c4d.SAVEPROJECT_ASSETLINKS_COPY_FILEASSETS
            | c4d.SAVEPROJECT_ASSETLINKS_COPY_NODEASSETS
            ) if not flags else flags

    assets = []
    missingAssets = []
    res = c4d.documents.SaveProject(doc, flags, file_path, assets, missingAssets)
    assert res, f"save_project_with_asset fail: {file_path}."
    
    new_doc = c4d.documents.GetActiveDocument()
    return new_doc


## TEXTURE OP
def texture_globalize(doc, allowDialogs=False):
    #将相对路径的贴图改成本地路径
    flags = c4d.ASSETDATA_FLAG_TEXTURESONLY | c4d.ASSETDATA_FLAG_NODOCUMENT | c4d.ASSETDATA_FLAG_MULTIPLEUSE
    assetList = []
    c4d.documents.GetAllAssetsNew(doc, allowDialogs, lastPath="", flags=flags, assetList=assetList)
    for i in assetList:
        if i["assetname"] != i["filename"]:
            baseList2D = i["owner"]
            if baseList2D.GetRealType() == 5833:
                baseList2D[c4d.BITMAPSHADER_FILENAME] = i["filename"] 
            elif baseList2D.GetType() == 1001101:#RS texture GetType() != GetRealType()
                baseList2D[c4d.REDSHIFT_SHADER_TEXTURESAMPLER_TEX0,c4d.REDSHIFT_FILE_PATH] =  i["filename"] 
            elif baseList2D.GetType() == 1036751:#RS Light GetType() != GetRealType()
                if baseList2D[c4d.REDSHIFT_LIGHT_TYPE] == 4:#dome
                    baseList2D[c4d.REDSHIFT_LIGHT_DOME_TEX0,c4d.REDSHIFT_FILE_PATH] = i["filename"] 
                elif baseList2D[c4d.REDSHIFT_LIGHT_TYPE] == 5:#IES
                    baseList2D[c4d.REDSHIFT_LIGHT_IES_PROFILE,c4d.REDSHIFT_FILE_PATH] = i["filename"] 
                else:#area/point
                    baseList2D[c4d.REDSHIFT_LIGHT_PHYSICAL_TEXTURE,c4d.REDSHIFT_FILE_PATH] = i["filename"]
            elif baseList2D.GetRealType() == 1036473:#corona
                baseList2D[c4d.CORONA_BITMAP_FILENAME] = i["filename"] 
            elif baseList2D.GetRealType() == 1029508:
                baseList2D[c4d.IMAGETEXTURE_FILE] = i["filename"] 
            elif baseList2D.GetRealType() == 1029508: # octane
                baseList2D[c4d.IMAGETEXTURE_FILE] = i["filename"] 
            else:
                print(f"[texture_globalize]{baseList2D}  还未添加该类型的贴图转换")
    c4d.EventAdd()


## RENDER
class RenderAgent:

    def __init__(self):
        self.progress = 0
        self.render_processing = boghma.utils.Signal("progress")
        self.render_finished = boghma.utils.Signal("progress")
        self.render_error = boghma.utils.Signal("progress")
        
    def render(self, doc, save_path=None, thread=None):
        self.progress = 0
        rd = doc.GetActiveRenderData()
        rd[c4d.RDATA_ALPHACHANNEL] = 1
        bmp = c4d.bitmaps.MultipassBitmap(int(rd[c4d.RDATA_XRES]), int(rd[c4d.RDATA_YRES]), c4d.COLORMODE_RGB)
        bmp.AddChannel(True, True)
        bmp.SetColorProfile(c4d.bitmaps.ColorProfile.GetDefaultSRGB())
        # Renders the document
        if thread:
            thread = thread.Get()
        
        if c4d.documents.RenderDocument(doc, rd.GetData(), bmp, c4d.RENDERFLAGS_EXTERNAL, thread, prog=self.PythonCallBack, wprog=self.PythonWriteCallBack) != c4d.RENDERRESULT_OK:
            #print("Failed to render the temporary document.")
            self.render_error.emit(self.progress)
            return False
        if save_path:
            bmp.Save(save_path, c4d.FILTER_PNG, data=None, savebits=c4d.SAVEBIT_ALPHA)
        self.render_finished.emit()
        return bmp

    def PythonCallBack(self, progress, progress_type):
        self.progress = float(int(progress*100))
        if self.progress>100:
            self.progress = 100
        self.render_processing.emit(self.progress)

    def PythonWriteCallBack(self, mode, bmp, fn, mainImage, frame, renderTime, streamnum, streamname):
        ...


## BMP
def get_bitmap_from(any_input):
    """将各种不同的值转换成bmp"""
    if isinstance(any_input, str): # file path
        bmp = c4d.bitmaps.BaseBitmap()
        bmp.InitWith(any_input)
        any_input = bmp
    elif isinstance(any_input, int):  # c4d icon id
        any_input = c4d.bitmaps.InitResourceBitmap(any_input)
    if isinstance(any_input, c4d.bitmaps.BaseBitmap):
        return any_input
    

## cmd line

def get_process_data(name="Cinema 4D"):
    """ 通过名称获取当前正在运行的软件信息"""
    info_list = []
    cmd = 'WMIC PROCESS get Caption,Commandline,Processid'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in proc.stdout:
        if name in str(line):
            s1 = str(line, encoding="utf-8")
            info_list = [] # ['Cinema 4D.exe', 'D:\\JACKADUX\\C4D S24\\Cinema 4D.exe', '31068']
            for i in s1.split("\""):
                info_list.append(i.strip())
            break
    return info_list

def kill_task(name="Cinema 4D"):
    """ 如果名称对应的软件正在运行, 则关闭软件"""
    info_list = get_process_data(name)
    try:
        if info_list:
            cmd = 'taskkill /pid ' + str(info_list[2]) + ' /f'
            os.system(cmd)
            return True
    except Exception as e:
        print(e)

def call_c4dpy(C4D_PATH, cmd):
    # 需要把c4dpy.exe所在路径添加到环境变量
    # C4D_PATH = r"~\Maxon Cinema 4D R26"
    if C4D_PATH not in os.environ["PATH"]:
        os.environ["PATH"]+=f"{C4D_PATH};"

    # cmd 也可以是脚本路径 cmd = r"~\c4dtest script.py" 
    _cmd = f"c4dpy \"{cmd}\"" # 脚本路径必须是字符串
    subprocess.call(_cmd) # 调用并且可以实时看到结果 

def creat_pypv(C4D_PATH, plugin_path):
    # pyp 生成 pypv
    # c4dpy.exe g_encryptPypFile="G:\C4D JACK Plugins\G4Designer\G4Designer.pyp"
    cmd = f"c4dpy g_encryptPypFile=\"{plugin_path}\""
    call_c4dpy(C4D_PATH, cmd)

# call_c4dpy(C4D_PATH=r"C:\Program Files\Maxon Cinema 4D R26", 
#            SCRIPT_PATH=r"D:\Wasabi\Pipeline Tool\test\c4dtest script.py")



































