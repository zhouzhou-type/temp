#coding: utf-8

#Module Import
import sys
import os
import MySQLdb

#全局变量
commitInfoTableID = 1

#数据库连接设置
dbHost = "localhost"
dbUser = "root"
dbpwd = "113425"
db = "Wine_Commit_Info"

#信息获取和处理
def commitInfoGetAndHandle():
    #获取commit信息
    cmd_0 = "git log > log.txt"
    os.popen(cmd_0)
    fileHandler = open('log.txt',mode = 'r',encoding = 'utf-8')
    retLines = fileHandler.readlines()
    #信息处理
    commitInfoHandle(retLines)

    
#log信息处理
def commitInfoHandle(retLines):
    conn = MySQLdb.connect(host=dbHost,user=dbUser,passwd=dbpwd,db=db,charset='utf8')
    print ("connect success")
    cursor = conn.cursor()
    commitInfoAdict = {} #数据字典，用于储存commit的基本信息
    commitInfoAdict["commit_times"] = 0 #处理第一个commit信息
    for line in retLines:
        line = line.replace("'",'"')
        #commit id获取
        commitLine = line.startswith("commit ") #commit+空格匹配
        if commitLine:
            if commitInfoAdict["commit_times"] != 0: #如果不是处理的第一个commit，则需要将上一个处理好的commit信息入库
                commitInfoSaveToDB(commitInfoAdict,cursor,conn) #commit信息入库
            commitInfoAdict["commit_times"] = commitInfoAdict["commit_times"] + 1 #遇到commit次数
            #分割处理
            line = line[len("commit "):len(line)].strip() #获取commit id
            if "(" in line:
                splitLine = line.split("(")
                commitIDinfo = splitLine[0].strip()
                commitIDs = commitIDinfo.split(" ")
                commitID = commitIDs[0]
            commitIDs = line.split(" ")
            commitID = commitIDs[0]
            #commitParentID = commitIDs[1] #父节点commit id 
            commitInfoAdict["CommitID"] = commitID #将commit id放入数据字典
        #author获取
        authorLine = line.startswith("Author") #Author匹配
        if authorLine:
            line = line[len("Author:"):len(line)].strip()
            commitInfoAdict["Author"] = line #将author放入数据字典
        #data获取
        dateLine = line.startswith("Date") #Date匹配
        if dateLine:
            line = line[len("Date:"):len(line)].strip()
            commitInfoAdict["Date"] = line #将date放入数据字典
        #commit message获取
        #messageLine = line.startswith()
        
                            
#commit信息入库

def commitInfoSaveToDB(commitInfoAdict,cursor,conn):
    global commitInfoTableID
    if ("CommitID" in commitInfoAdict) and ("Author" in commitInfoAdict) and ("Date" in commitInfoAdict):
        commitID = commitInfoAdict.pop("CommitID")
        author = commitInfoAdict.pop("Author")
        age = commitInfoAdict.pop("Date")
        #commitMessage = commitInfoAdict.pop("Message")
        sql = "insert into Commit_Info_Table(id,commitID,author,age) values(%s,'%s','%s','%s')" % (commitInfoTableID,commitID,author,age)
        cursor.execute(sql)
        conn.commit()
        commitInfoTableID += 1
        
if __name__ == "__main__":
    commitInfoGetAndHandle()