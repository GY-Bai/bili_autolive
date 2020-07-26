# -*- coding: utf-8 -*-
"""
Created on Mon Jul 20 09:35:52 2020

@author: baige
"""
#%%
import time,datetime,os,re
import pandas as pd
import numpy as np
import ffmpy 
import shutil
import subprocess
import json
import pexpect
import progressbar
import logging



rootdir=r'D:\文档\录播机'


    
def collectflv1(rootdir):
    L=[]   
    for dirpath, dirnames, filenames in os.walk(rootdir):  
        for file in filenames :  
            if os.path.splitext(file)[1] == '.flv':  
                L.append(os.path.join(dirpath, file)) 
    if len(L) >0 :
        flvtable=pd.DataFrame(L)
        flvsize=[]
        for a_flv in L:
            tmpsize=get_FileSize(a_flv)
            flvsize.append(tmpsize)
        flvtable.columns=['flv']
        flvtable['latestsize']=flvsize
    else:
        flvtable=pd.DataFrame()
    return flvtable

def collectflv2(flvtable,rootdir): 
    
    flvtable=flvtable.reset_index(drop=True)
    flvtable['oldsize']=flvtable['latestsize']
    for dirpath, dirnames, filenames in os.walk(rootdir):  
        for file in filenames :  
            if os.path.splitext(file)[1] == '.flv': 
                flvfulldir=os.path.join(dirpath, file)
                # 第二次运行的话，应该刷新table内部数据了
                
                oldflvindex = flvtable[(flvtable['flv']==flvfulldir)].index.tolist()
                if len(oldflvindex) != 0: 
                    flvtable.iloc[oldflvindex,1]=get_FileSize(flvfulldir)
                else:
                    tmptable=pd.DataFrame([{'flv':flvfulldir,'latestsize':get_FileSize(flvfulldir),'oldsize':np.NaN}])
                    flvtable=pd.concat([flvtable,tmptable], ignore_index=True)
    return flvtable
                


        
        
def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize/float(1024*1024)
    return round(fsize,2)

def yazhi(flvtable,rootdir):
    #先查找没有压制标识的
    yazhi_list=[]
# =============================================================================
#     for dirpath, dirnames, filenames in os.walk(rootdir):  
#         for file in filenames :  
#             if os.path.splitext(file)[1] == '.flv':
#                 if os.path.splitext(file)[0].find('YZ') ==-1 and os.path.splitext(file)[0].find('HB') == -1:
#                     yazhi_list.append(os.path.join(dirpath, file))
# =============================================================================
    for index in range(len(flvtable)):
        tmpline=flvtable.iloc[index,:]       
        if tmpline[1]-tmpline[2] == 0 and tmpline[0].split('\\')[-1].find('YZ') ==-1 and tmpline[0].split('\\')[-1].find('HB') == -1:
            yazhi_list.append(tmpline[0])
             
    #对没有压制标识的进行压制
    
    for a_flv in yazhi_list:
        yazhiname=a_flv[:-4]+'YZ'+a_flv[-4:] 
        flvuseless=r'D:\文档\录播垃圾桶\\'+a_flv.split('\\')[-1]
        try:
            
            if getLength(a_flv) > 1280:
               
                ff = ffmpy.FFmpeg(
                     inputs={a_flv: None},
                     outputs={yazhiname: ['-c:v','libx264','-b:v', '1800k', '-profile:v' ,'main']} )
            
            else:
                ff = ffmpy.FFmpeg(
                     inputs={a_flv: None},
                     outputs={yazhiname: ['-c:v','libx264','-b:v', '1700k', '-profile:v' ,'main']} )
        except:
            
            print("压制姬：貌似又是读取分辨率出现了问题。[强制执行720p的压制参数]。。。。。。。。")
            time.sleep(60)
            ff = ffmpy.FFmpeg(
                     inputs={a_flv: None},
                     outputs={yazhiname: ['-c:v','libx264','-b:v', '1700k', '-profile:v' ,'main']} )
        
        kk=ff.cmd
        print("正在压制："+a_flv)
        tf = os.popen (kk)
        print(tf.read())
        mymovefile(a_flv,flvuseless)
        print("压制成功："+flvuseless)
        

def getLength(filename):
    command = ["ffprobe.exe","-loglevel","quiet","-print_format","json","-show_format","-show_streams","-i",filename]
    result = subprocess.Popen(command,shell=True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    out = result.stdout.read()
    temp = str(out.decode('utf-8'))
    try:
        data = json.loads(temp)['streams'][1]['width']
    except:
        data = json.loads(temp)['streams'][0]['width']
    return data

def getLenTime(filename):
    command = ["ffprobe.exe","-loglevel","quiet","-print_format","json","-show_format","-show_streams","-i",filename]
    result = subprocess.Popen(command,shell=True,stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
    out = result.stdout.read()
    #print(str(out))
    temp = str(out.decode('utf-8'))
    data = json.loads(temp)["format"]['duration']
    return data


def mymovefile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print ("%s not exist!")
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.move(srcfile,dstfile)          #移动文件
        print ("move "+srcfile+" -> "+dstfile)

#%%
print('当你看到这条消息，代表压制姬已经被成功激活了！')
while 1:
    flvtable=collectflv1(rootdir)
    time.sleep(60)
    
    
    if len(flvtable) >0 :#列表里有东西
        flvtable=collectflv2(flvtable,rootdir)
        
        panduan_raw=[]
        for index in range(len(flvtable)):
            tmpline=flvtable.iloc[index,:]       
            if tmpline[1]-tmpline[2] == 0 and tmpline[0].split('\\')[-1].find('YZ') ==-1 and tmpline[0].split('\\')[-1].find('HB') == -1:
                panduan_raw.append(tmpline[0])
        print(panduan_raw)
        if len(panduan_raw) > 0 :#而且列表里有未压制的源文件
            print("压制姬：发现新活，正在缓慢起床准备。   ︿(￣︶￣)︿  ")
            yazhi(flvtable,rootdir)
            
        else:
            print("压制姬：无所事事，游手好闲中。[当前有文件，但是没有可供压制的RAW文件（也有可能是正在直播）]。。。。。。。。")
            time.sleep(60*10)
        
        
    else:
        print("压制姬：无所事事，游手好闲中。[当前没有任何视频文件，甚至连压制和合并过的文件都没有]。。。。。。。。")
        time.sleep(60*10)
#%%


