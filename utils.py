# -*- coding: utf-8 -*-

import threading  # 用于多线程工作
import pickle
import random
import os
import json

pickle_dir = 'pickle/'
log_dir = 'log/'
news_dir = 'news_log/'
sleeptime_L = 5*60
sleeptime_S = 5*60
mu =  threading.RLock()
logfile = log_dir + 'watch.log'
label = ' # news watch # '

if not os.path.exists("sendSuccessNews.json"):
    os.system(r"touch {}".format("sendSuccessNews.json"))
if not os.path.exists(pickle_dir):
    os.mkdir(pickle_dir)
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
if not os.path.exists(news_dir):
    os.mkdir(news_dir)
if not os.path.exists(logfile):
    # 调用系统命令行来创建文件
    os.system(r"touch {}".format(logfile))
f = open(logfile,'a+')
pricklefileName = pickle_dir + '监控数据_热启动文件.pickle'
if not os.path.exists(pricklefileName):
    # 调用系统命令行来创建文件
    os.system(r"touch {}".format(pricklefileName))

Master = {'Master':{'UserName':'', 'NickName':'xiaoyuan'}}
Debug = False
sendSuccessList = [] # 记录发送成功的新闻，每一条新闻是一个字典 防止重复发送了


def syncNews2File():
    jsObj = json.dumps(sendSuccessList, ensure_ascii=False)
    with open('sendSuccessNews.json', 'w') as f:
        f.write(jsObj)


def getSendSuccessNews():
    with open("sendSuccessNews.json", "r") as f:
        lJson = f.read()
        if len(lJson):
            global sendSuccessList
            sendSuccessList = json.loads(lJson)
            print(len(sendSuccessList))

#--------------------------------操作用户列表-------------------------------------------#
def SendAlert2Master( errmsg):
    global logfile, label, Master
    errmsg2 = '程序异常，提醒管理员：\n' + str(errmsg)
    write2Log(str(label) + str(errmsg2))
    #WeChat.SendWeChatMsgToUserList(Master, errmsg2, logfile)
    print(str(label) + str(errmsg2))
def write2Log(msg):
    global f,logfile
    try:
        if f.closed:
            f = open(logfile,'a+')
        f.write(msg + '\n')
        f.close()
    except Exception as e:
        raise Exception('# 异常：监控程序：write to log error!' + str(e))



def showSleepTime():
#     \'getslt\'： \t 显示扫描间隔时间
    global sleeptime_L, sleeptime_S
    return '#两次扫面时间间隔# 休市时： '  + str(sleeptime_L) + ' s，开市时：' + str(sleeptime_S) + ' s !'
def setSleepTime(paras):
 #   \'setslt 10\'： \t 设置休眠时间为 10 s
    global sleeptime_L, sleeptime_S
    if len(paras)!=3:
        Output = '# 错误: ' + str(label) + ' setSleepTime(), 参数错误！\n' + str(paras) + '\n'
        Output = Output + '向用户发通知：\n \'setslt 900 60\'： \t 设置休眠时间为分别为900 s（休市），60 s（开市）   ！'
        print(paras)
    else:
        Output = ''
        time_l = float(paras[1])
        time_s = float(paras[2])
        try: # 首先，检查用户是否在列表中
            if time_s < 0.01 or time_l < 0.01: # 太短休息时间还不如不休息呢，是不是
                Output = '休息时间太短，不干！'
            else:
                sleeptime_L = time_l
                sleeptime_S = time_s
                Output = '休市时扫描间隔设置为 '  + str(time_l) + ' s，开市时扫描间隔设置为：' + str(time_s) + ' s !'
            return Output
        except Exception as e:   # 如果账号不成功，什么也不做，并返回消息
            Output = '# 两次扫描间隔时间设置异常: ' + str(e)
            write2Log(Output)
            print(Output)
            SendAlert2Master(Output)
    return Output
def pickleDump2file(UserList, filename):
    try:
        with mu:
            data = {}
            for callName in UserList.keys():
                user = UserList[callName]
                news = False
                stock = False
                if UserList[callName]['Stock']:
                    stock = True
                if UserList[callName]['News']:
                    news = True
                data.setdefault(callName, {'UserName':user['UserName'], 'NickName':user['NickName'], 'Stock':stock, 'News':news})
        # 只写入 callName, UserName, NickName
            with open(filename, 'wb') as f:
                pickle.dump(data, f)
                print(label + '消息：pickle file写入成功！')
                write2Log(label + '：pickle file写入成功！')
    except Exception as e:
        print(label + '：pickle file写入异常！'+ str(e))
        write2Log(label + '：pickle file写入异常！')
def getDatafromPickle(filename):
    Flag = False
    try:
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            Flag = True
            print(label + '：pickle file读取成功！')
            write2Log(label + '：pickle file读取成功！')
    except Exception as e:
        Flag = False
        data = label + '热启动失败！开始初始化  ' + str(e)
        print(data)
        write2Log(data)
    return Flag, data


# 默认的User-Agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6"

# 加载当前目录的绝对路径
install_folder = os.path.abspath(os.path.split(__file__)[0])
# 加载当前目录下的user-agents.txt文件
user_agents_file = os.path.join(install_folder, 'user-agents.txt')

try:
    with open(user_agents_file) as f:
        user_agent_list = [_.strip() for _ in f.readlines()]
except:
    user_agent_list = [USER_AGENT]

def get_random_user_agent():
    '''
    随机获取一个User-Agent
    :return:
    '''
    return random.choice(user_agent_list)