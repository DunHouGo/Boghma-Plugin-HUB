# -*- coding: utf-8 -*-
import os
import json
import shutil
import zipfile
import uuid
try:
    import c4d
except:
    pass


def __copy_to_use():
    import datetime, time
    ct = time.strftime("%Y-%m-%d %H:%M:%S")
    datetime.datetime.strptime(ct, "%Y-%m-%d %H:%M:%S")


def gethostname():
    import re, socket
    return re.sub("\W", "_", socket.gethostname()) # 获取当前主机名

def get_uuid4():
    uid = str(uuid.uuid4())
    suid = ''.join(uid.split('-'))
    return suid

def get_uuid5(string):
    ids = uuid.uuid5(uuid.NAMESPACE_DNS, string)
    ids = str(ids).replace("-", "")
    return str(ids)

def get_subfiles(source_path):
    if os.path.exists(source_path):
        return os.listdir(source_path)

def folder_and_file(source_path):
    return os.path.basename(source_path), os.path.dirname(source_path)

def makedirs(source_path):       
    if os.path.isfile(source_path):
        raise ValueError(f"source_path must be dircfolder path not: {source_path}")
    if not os.path.exists(source_path):                               
        os.makedirs(source_path)

#file
def read_file(source_path):
    if not os.path.exists(source_path):
        raise RuntimeError("path not exists")
    with open(source_path, 'r', encoding='UTF-8') as file:
        strings = file.read()
    file.close()
    return strings

def write_file(source_path, data):
    with open(source_path, 'w', encoding='UTF-8') as file:
        file.write(data)
    file.close()

#json
def json_dupms(data):
    strings = json.dumps(data, sort_keys=True, indent=4,
                         separators=(', ', ':'), ensure_ascii=0)
    return strings

def json_loads(strings):
    json_data = json.loads(strings)
    return json_data

def read_json(source_path):
    return json_loads(read_file(source_path))

def write_json(source_path, data):
    write_file(source_path, json_dupms(data))

#hyperfile
def convert_json2container(data):
    strx = json_dupms(data)
    bc = c4d.BaseContainer()
    bc[1000] = strx
    return bc

def convert_container2json(container_data):
    strx = container_data[1000]
    data = json_loads(strx)
    return data

def read_hyperfile(key, path):
    hf = c4d.storage.HyperFile()
    if hf.Open(ident=key, filename=path, mode=c4d.FILEOPEN_READ, error_dialog=c4d.FILEDIALOG_NONE):
        bc = hf.ReadContainer()
        hf.Close()
        return bc
    else:
        return False

def write_hyperfile(key, path, data):
    hf = c4d.storage.HyperFile()
    if hf.Open(ident=key, filename=path, mode=c4d.FILEOPEN_WRITE, error_dialog=c4d.FILEDIALOG_NONE):
        hf.WriteContainer(data)
        hf.Close()
    else:
        return False
    
# file op

def copy_file(source_path, target_folder_path, change_name=""):
    cond = os.path.exists(source_path) and os.path.isfile(source_path)
    assert cond, f"source_path must be a exists file path, not {source_path}"
    cond2 = os.path.exists(target_folder_path) and os.path.isdir(target_folder_path)
    assert cond2, f"target_folder_path must be a exists folder path, not {target_folder_path}"
    
    name = os.path.basename(source_path)
    if change_name:
        name = change_name + "."+name.split(".")[-1]
    target_path = os.path.join(target_folder_path, name)
    shutil.copy(source_path, target_path)
    return target_path
    
def copy_folder(source_folder_path, target_folder_path):
    cond = os.path.exists(source_folder_path) and os.path.isdir(source_folder_path)
    assert cond, f"source_folder_path must be a exists folder path, not {source_folder_path}"
    cond2 = os.path.exists(target_folder_path) and os.path.isdir(target_folder_path)
    assert cond2, f"target_folder_path must be a exists folder path, not {target_folder_path}"
    
    name = os.path.basename(source_folder_path)
    target_path = os.path.join(target_folder_path, name)
    makedirs(target_path)
    for subfile in os.listdir(source_folder_path):
        file_path = os.path.join(source_folder_path, subfile)
        if os.path.isfile(file_path):
            copy_file(file_path, target_path)
        elif os.path.isdir(file_path):
            copy_folder(file_path, target_path)
        else:
            print("copy_folder : file is Unknow type")
    return target_path

def delet_file(source_path):
    cond = os.path.exists(source_path) and os.path.isfile(source_path)
    assert cond, f"source_path must be a exists file path, not {source_path}"
    os.remove(source_path)

def delet_folder(source_folder_path):
    cond = os.path.exists(source_folder_path) and os.path.isdir(source_folder_path)
    assert cond, f"source_folder_path must be a exists folder path, not {source_folder_path}"

    for file in os.listdir(source_folder_path):
        file_path = os.path.join(source_folder_path, file)
        if os.path.isfile(file_path):
            delet_file(file_path)
        elif os.path.isdir(file_path):
            delet_folder(file_path)
        else:
            print("delet_folder : file is Unknow type")
    os.rmdir(source_folder_path)
    return

def zip_file(source_path):
    if not os.path.exists(source_path):
        return False

    basename = os.path.basename(source_path)
    dirname = os.path.dirname(source_path)
    if os.path.isfile(source_path):
        zip_name = basename.split(".")[0]
        output_filename = os.path.join(dirname, zip_name+".zip")
    if os.path.isdir(source_path):
        output_filename = source_path+".zip"
    zipf = zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED)
    pre_len = len(dirname)
    for parent, dirnames, filenames in os.walk(source_path):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)
            zipf.write(pathfile, arcname)
        for dirname in dirnames:
            dirfile = os.path.join(parent, dirname)
            arcname = dirfile[pre_len:].strip(os.path.sep)
            zipf.write(dirfile, arcname)

    zipf.close()
    return output_filename

def unzip_file(source_path):
    if not os.path.exists(source_path):
        return False
    if os.path.isdir(source_path):
        return False
    dirname = os.path.dirname(source_path)
    zip_file = zipfile.ZipFile(source_path)
    for names in zip_file.namelist():
        try:
            zip_file.extract(names, dirname)
        except Exception as err:
            print("funfile.unzip error: ", err)
    zip_file.close()
    return True


# ----

def _rename_file(source_path, new_name):
    if not os.path.exists(source_path):
        return False

    bn, dn = folder_and_file(source_path)
    if os.path.isfile(source_path):
        ends = bn.split(".")
        if len(ends) > 1:
            end = ends[-1]
        else:
            end = ""
        new_name += "."+end
    dst = os.path.join(dn, new_name)
    if os.path.exists(dst):
        delet_file(dst)
    os.rename(source_path, dst)
    return dst


def _dyn_importlib():
    import os
    import importlib

    Path, f = os.path.split(__file__)
    for file in os.listdir(Path):
        if file[0] == "_" or not file.endswith(".py"):
            continue
        modname = file.split(".")[0]
        mod_obj = importlib.import_module("Jlibsv2."+modname)
        importlib.reload(mod_obj)    