# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 06:32:52 2020

@author: baige
"""


#%%
import time,datetime,os,re
import threading
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
rubbish=r'D:\文档\录播垃圾桶'
tmppath=r'D:\ffmpeg\tmp_live\HB'




def mymovefile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print ("%s not exist!")
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.move(srcfile,dstfile)          #移动文件
        print ("move "+srcfile+" -> "+dstfile)


HB_flvlist=[]
HB_pathlist=[]

for dirpath, dirnames, filenames in os.walk(rootdir):
    HB_pathlist.append(dirpath)
    HB_flvlist.append(filenames)

tmpfilelist=[]
for files in HB_flvlist :
    tmpgroup=[]
    for a_file in files :
        if  a_file.find('.flv') !=-1 :
            tmpgroup.append(a_file)
    tmpfilelist.append(tmpgroup)
    
HB_flvlist=tmpfilelist
    
del HB_flvlist[0]
del HB_pathlist[0]
count=0
count_list=[]
gaiming_list=[]
for a_flvlist in HB_flvlist :
    if len(a_flvlist) > 1 :
        count_list.append(count)
    else:
        if len(a_flvlist) == 1 :
            gaiming_list.append(count)
    count = count + 1
#%%
for a_count in count_list :
    tmpflvname=HB_flvlist[a_count]
    tmpflvname=pd.DataFrame(tmpflvname,columns=['flvname'])
    if len(tmpflvname.loc[tmpflvname['flvname'].str.contains('YZ')]) != len(tmpflvname):
        print('还有未转码文件，请耐心等待转码！')
    else:
        tmpflvname['tmp']=tmpflvname['flvname']
        tmpflvname['tmp']=tmpflvname['tmp'].str.replace('YZ','')
        tmpflvname['tmp']=tmpflvname['tmp'].str.replace('.flv','')
        tmpflvtime=tmpflvname['tmp'].str.split('-',expand=True)
        tmpflvname['livestart']=tmpflvtime[1]+tmpflvtime[2]
        tmpflvname.sort_values(by=['livestart'])
        print(tmpflvname)
        outputname=tmpflvtime[0].tolist()[-1]+'-'+tmpflvtime[1].tolist()[0]+'-'+tmpflvtime[2].tolist()[0]+'HB.flv'
        outputname_pureE=tmpflvtime[1].tolist()[0]+'-'+tmpflvtime[2].tolist()[0]+'HB.flv'
        inputname=tmpflvname['flvname'].tolist()
        path=HB_pathlist[a_count]
        for flvname in inputname:
            fullname=path+'\\'+flvname
            
            flvindex=tmpflvname[(tmpflvname['flvname']==flvname)].index.tolist()[0]
            
            tmpyz=tmppath+'\\'+str(flvindex)+'.flv'
            mymovefile(fullname,tmpyz)
        
        
        
        txtpath=tmppath+"\\a.txt"
        f = open(txtpath, 'w')
        for flvname in inputname:
            flvindex=tmpflvname[(tmpflvname['flvname']==flvname)].index.tolist()[0]
            
            tmpyz=tmppath+'\\'+str(flvindex)+'.flv'
            fulline="file '"+tmpyz+"'\n"
            f.write(fulline)
        f.close()
        
        ffmpg='ffmpeg -f concat -safe 0 -i '+txtpath+' -c copy '+tmppath+'\\'+outputname_pureE
        #%%
        print("正在合并："+txtpath)
        tf = os.popen (ffmpg)
        #%%
        for flvname in inputname:
            flvindex=tmpflvname[(tmpflvname['flvname']==flvname)].index.tolist()[0]
            tmpyz=tmppath+'\\'+str(flvindex)+'.flv'
            flvuseless=rubbish+'\\'+flvname
            mymovefile(tmpyz,flvuseless)
        mymovefile(tmppath+'\\'+outputname_pureE,path+'\\'+outputname)
        print('-------------------------------------')
        print("合并成功："+path+'\\'+outputname)
#%%
for a_count in gaiming_list :
   tmpflvname=HB_flvlist[a_count]
   tmpflvname=pd.DataFrame(tmpflvname,columns=['flvname'])
   if len(tmpflvname.loc[tmpflvname['flvname'].str.contains('YZ')]) != len(tmpflvname):
       print('还有未转码文件，请耐心等待转码！')
   else:       
        inputname=tmpflvname['flvname'].tolist()
        path=HB_pathlist[a_count]
        for flvname in inputname:
            fullname=path+'\\'+flvname
            gaiming=path+'\\'+flvname.replace('YZ.flv','')+'HB.flv'
            mymovefile(fullname,gaiming)
            print("改名完成："+gaiming)
        
        
        
        
        
        
        
        
        
        
