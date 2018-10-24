#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import shutil
import traceback
# 获取指定目录下第一级子文件夹名
def get_subdir(path): 
    print(path)
    if os.path.exists(path):
        print('exist')
        subdir_names=[]
        names = os.listdir(path)
        for name in names:
            name_with_path=os.path.join(path,name)
            if os.path.isdir(name_with_path):
                subdir_names.append(name)
        return subdir_names

# 获取指定目录下第一级子文件名
# @file_postfix 获取文件后缀list
def get_subfile(path,file_postfix): 
    if os.path.exists(path):
        subfile_names=[]
        names = os.listdir(path)
        for name in names:
            if ( not(os.path.isdir(name)) and (name in file_postfix) ) :
                subfile_names.append(name)
                
        return subdir_names

# # 获取文件名
# # todo 匹配多个后缀
# def file_name(file_dir,file_postfix):  
#   files_name=[]  
#   for root, dirs, files in os.walk(file_dir): 
#     for file in files: 
#       if os.path.splitext(file)[1] in file_postfix: 
#         files_name.append(file) #os.path.join(root, file)
#   return files_name

# 删除路径下文件夹
# @path 路径
# @ignore_dir  忽略文件夹
def rm_dir(path,ignore_dir):  
    try:
        dirs=get_subdir(path)
        for dir in dirs:
            if dir in ignore_dir:
                continue
            else:
                rm_dir_path=os.path.join(path,dir)
                shutil.rmtree(rm_dir_path)
    except Exception as e:
        traceback.print_exc()   