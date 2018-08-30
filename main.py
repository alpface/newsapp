# -*- coding: utf-8 -*-

import newswatch as ns
from utils import log_dir, pickle_dir, news_dir
import utils as MasFun
import threading
import time, os
from threading import Timer
import datetime
from utils import logfile, label, pricklefileName, f

timer_t = None
mu =  threading.RLock()
global __Author__
global Master
__Author__ = 'xiaoyuan'
Master = {'Master':{'UserName':'', 'NickName':'xiaoyuan'}}
UserList = {'xiaoyuan':{'UserName':'', 'NickName':'xiaoyuan', 'Stock':None, 'News':None},\
            }   #初始用户列表

global initMsg

initMsg = '监控软件 by ' + str(__Author__) + ' 启动！\n'

Debug = MasFun.Debug
# 如新闻列表获取失败，信息没有查到，只需要返回错误给用户，并通知管理员
def SendOnlineMsg(entertime):
    global Master, logfile, timer_t
    try:
        reply = '现在时间是： ' + datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S')
        # SendWeChatMsgToUserList(Master, reply + '！\n瓦力在线，继续努力工作中！', logfile)
        timer_t = Timer(3600*4, SendOnlineMsg, ( time.time(), )) # 间隔时间,4 小时发一次
        timer_t.start()  
    except Exception as e:
        raise Exception('# 异常：向管理员发送值班信息异常：' + str(e))   
def write2Log(msg):
    global f,logfile, Master
    try:
        if f.closed:
            f = open(logfile,'a+')
        f.write(msg + '\n')
        f.close()
    except Exception as e:
        errmsg = '# 监控程序日志写入异常：write to log error!' + str(e)
        print(errmsg)
def __Init__():
    """
    用户列表监控类的初始化
    """
    global Master, logfile, UserList, pricklefileName, Debug
    print(initMsg)
    write2Log(initMsg)

    hotReload = False
    if not Debug:
       hotReload, data = MasFun.getDatafromPickle(pricklefileName)
       # try:
       #     WeChatgetDatafromPickle()
       # except Exception:
       #     pass
    if hotReload:
        UserList = data
    try:
        with mu:
            for user in UserList:  
                print(user)
                # 初始化用户的监控类
                if (not hotReload) or (hotReload and UserList[user]['News']): # 如果冷启动，或者热启动时，原有文件中含有News
                    UserList[user]['News'] = ns.TBaiDuNewsScapper(user, UserList[user]['NickName'], hotReload)
    except Exception as e:  # 初始化时，属于严重错误，向上抛出异常
        raise Exception(str(e))
def Run():
    """
    1. 依次运行用户的两个监控程序
    2. 如果监控程序出错，则处理异常，且向管理员发信息
    
    """
    global Master, logfile, label
    try:
            
        print('\n# 运行一次监测程序 #')
        tempNewsObject = None # 检测新闻的对象
        for user in UserList:
            print('\n#------------------用户： ' + str(user) + ' ---------------------------#\n')
            # if UserList[user]['Stock']:
            #     UserList[user]['Stock'].Run()
            #     tempStockObject = UserList[user]['Stock']
                
            if UserList[user]['News']:
                UserList[user]['News'].Run()
                tempNewsObject = UserList[user]['News']
        if tempNewsObject and tempNewsObject.OnDuty():
            time.sleep(MasFun.sleeptime_L)  #休息sleeptime_L时间再爬取
        else:
            time.sleep(MasFun.sleeptime_S)  #暂停一段时间,休市
    except KeyboardInterrupt: # 正常键盘退出
        errmsg = '监控程序异常，提醒管理员：\n 键盘中断，微信退出!'
        raise KeyboardInterrupt(errmsg)
    except Exception as e: # 一般错误, 继续运行
        errmsg = label + '运行异常： ' + str(e)
        print(errmsg)
        write2Log(errmsg)
        return
    
def runAllNewsWatch(entertime):
    global label, timer_news
    try:
        with mu:
            for user in UserList:
                print('\n#------------------用户： ' + str(user) + ' ---------------------------#\n')
                if UserList[user]['News']:
                    UserList[user]['News'].Run()
        timer_news = Timer(MasFun.sleeptime_L, runAllNewsWatch, ( time.time(), )) 
        timer_news.start()            
    except KeyboardInterrupt: # 正常键盘退出
        errmsg = '监控程序异常，提醒管理员：\n 键盘中断，微信退出!'
        raise KeyboardInterrupt(errmsg)
    except Exception as e: # 一般错误, 继续运行
        errmsg = label + '运行异常： ' + str(e)
        print(errmsg)
        write2Log(errmsg)
def runAllStockWatch(entertime):
    global label, timer_stock
    try:
        with mu:
            tempStockObject = None
            for user in UserList:
                print('\n#------------------用户： ' + str(user) + ' ---------------------------#\n')
                if UserList[user]['Stock']:
                    UserList[user]['Stock'].Run()
                    tempStockObject = UserList[user]['Stock']
        if tempStockObject and tempStockObject.OnDuty():
            timer_stock = Timer(MasFun.sleeptime_S, runAllStockWatch, ( time.time(), )) 
            timer_stock.start()             
        else:
            timer_stock = Timer(MasFun.sleeptime_L, runAllStockWatch, ( time.time(), )) 
            timer_stock.start() 
    except KeyboardInterrupt: # 正常键盘退出
        errmsg = '监控程序异常，提醒管理员：\n 键盘中断，微信退出!'
        raise KeyboardInterrupt(errmsg)
    except Exception as e: # 一般错误, 继续运行
        errmsg = label + '运行异常： ' + str(e)
        print(errmsg)
        write2Log(errmsg)   
    
def Bye():
    """
    1. 每个用户两个监控程序的退出
    """
    global mu, UserList, pricklefileName, Debug
    try:
        timer_t.cancel()
#        timer_news.cancel()
#        timer_stock.cancel()
        with mu:
            # 写入主账户的用户名和昵称
            # if not Debug:
            #     MasFun.pickleDump2file(UserList, pricklefileName)
            #     WeChatpickleDump2file()
            # 先将所有用户信息写入文件
            # print('\n正在写入用户信息：\n')
            # fileName  = news_dir + 'UserInfo' + str(time.strftime('_%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))) + '.txt'
            # f = open(fileName,'w+')
            # f.write(MasFun.listAllUsers(UserList) + '\n')
            # f.close()
            # print('\n用户信息写入完成！\n')
            for user in UserList:
                if UserList[user]['Stock']:
                    UserList[user]['Stock'].Bye(Debug)
                    UserList[user]['Stock'] = None
                if UserList[user]['News']:
                    UserList[user]['News'].Bye(Debug)
                    UserList[user]['News'] = None
    except Exception as e:
        errmsg = label + ' 退出异常：' + str(e)
        write2Log(errmsg)


if __name__=="__main__":
    try:
        __Init__()
    except Exception as e:  # 处理异常
        errmsg = '# 这个监控程序初始化异常！' + str(e)
        print(errmsg)
        write2Log(errmsg)
        os._exit()
        
    #
    try:
        Timer(0, SendOnlineMsg, ( time.time(), )).start()  
        while True:
            Run()
    except KeyboardInterrupt as e: # 正常键盘退出
        errmsg = str(e)
        print(errmsg)
        write2Log(errmsg)
        Bye()
