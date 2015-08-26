# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import os
import urllib2,json,time
from lxml import etree
from dbm import dbm

class message:
    
    def __init__(self):
        self.app_root = os.path.dirname(__file__)
        self.templates_root = os.path.join(self.app_root, 'templates')
        self.render = web.template.render(self.templates_root)
        self.recordDict = {}
        self.recordDict[3] = {1:10,2:13,3:15,4:18,5:19,6:16,7:12,8:11}
        
        #设置组队和关卡的个数
        self.teamNum = 50
        self.pointNum = 8
        self.tableTag = 'point'
        self.perPointScore = 500
        #服务器设置
        self.sqlServer = dbm()
        #self.listTableName = [self.tableTag +str(i) for i in xrange(1,self.pointNum+1)]
        '''
        try:
            strParam = '(tablename char(200) primary key, username char(200))'
            flag=self.sqlServer.creat_table_name('usertablerelation',strParam)
            if flag == "you have registered or table is exist":
                print u'table is exist'
            elif flag ==False:
                print u'table build fail'
            else:
                print "table build ok"
        except Exception, e:
            print e 
        '''
        
    def GET(self):
        #获取输入参数
        data = web.input()
        signature=data.signature
        timestamp=data.timestamp
        nonce=data.nonce
        echostr=data.echostr
        #自己的token
        token="weishichao121" #这里改写你在微信公众平台里输入的token
        #字典序排序
        listTemp=[token,timestamp,nonce]
        listTemp.sort()
        sha1=hashlib.sha1()
        map(sha1.update,listTemp)
        hashcode=sha1.hexdigest()
        #sha1加密算法

        #如果是来自微信的请求，则回复echostr
        if hashcode == signature:
            return echostr
        
    def POST(self):
        str_xml = web.data() #获得post来的数据
        xml = etree.fromstring(str_xml)#进行XML解析
        
        self.sendfromUser=xml.find("FromUserName").text
        self.fromUser = self.sendfromUser.replace('-','11')
        self.toUser=xml.find("ToUserName").text
        
        try:
            msgType=xml.find("MsgType").text
            if msgType == 'event':
                EventKey = xml.find("EventKey").text
                retMsg = self.handleEvent(EventKey)
            elif msgType != u'text':
                retMsg = u'请输入text类型，不要输入'+msgType+u'类型'
            else:
                content=xml.find("Content").text#获得用户所输入的内容
                retMsg = self.handleMsg(content)
        except Exception,e:
            #retMsg = u'无法识别类型'
            retMsg = unicode(e)
        
        return self.replyMsgToUser(retMsg)
    
    def handleEvent(self,EventKey):

        if EventKey == u'RANKING':
            retMsg = self.getRanking()
        elif EventKey == u'':
            retMsg = u'欢迎关注“华三跑协”公众号平台测试号'
        else:
            retMsg = EventKey
            
        return retMsg
        
    
    def handleMsg(self,msg):
        
        # 主要工作内容在本函数
		# msg为用户输入内容
		# replyMsg为回复内容
		# 本函数做各种逻辑运算，存储
		# 默认回复为用户输入的内容
        
        #replyMsg = msg
        if msg.startswith(u'注册+'):
            replyMsg = self.create_and_initTable(msg)
        elif msg == u'注销':
            replyMsg = self.delete_Table()
        elif msg.startswith(u'完成+'):
            replyMsg = self.addUserData(msg)
        elif msg == u'查询':
            replyMsg = self.getUserData()
        elif msg == u'总排名':
            replyMsg = self.getRanking()
        elif msg.startswith(u'月排名+'):
            replyMsg=self.getmonthRanking(msg)
        elif msg == 'user':
            replyMsg = 'fromUser:' + self.sendfromUser + '\ntoUser:' + self.toUser
        elif msg == u'找回注册号':
            replyMsg = self.getregisternum()
        elif msg == u'帮助':
            replyMsg = '例如:\n用户注册:注册+liushufang\n用户注销:注销 \n数据添加:完成+10\n数据查询:查询\n总排名查询:总排名\n月排名查询：月排名+201507\n找回注册号:找回注册号'
                                                                            
        else:
            replyMsg = '输入‘帮助’查看帮助信息\n'
            
        # 回复用户的内容为replyMsg
        return replyMsg
    
    def getregisternum(self):
        try:
            result = self.sqlServer.get_table_value(self.fromUser)
        except:
            return u"请先注册"
        for tempResult in result:
            if tempResult[-1] == -1:
                userName = tempResult[0]
                break
            else:
                continue
        return u'你的注册号是：'+userName
            
    
    def replyMsgToUser(self,retMsg):
        return self.render.reply_text(self.sendfromUser,self.toUser,int(time.time()),retMsg)
    
    def getLocalTime(self):
        
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    
    def getUserData(self):
        
        try:
            result = self.sqlServer.get_table_value(self.fromUser)
        except:
            return u"请先注册"
        
        printStr = u'\n'
        printTotal = u'总成绩:'
        userName = u''
        totalScore = 0
		
        for tempResult in result:
            if tempResult[-1] == -1:
                userName = tempResult[0]
            else:
                tempTime = tempResult[1]
                tempScore = tempResult[2]
                totalScore += tempScore
                printStr += tempTime[:10] + '----' + str(tempScore) + 'km\n'
        
        printStr = userName + ':\n' + printTotal + str(totalScore) + 'km' + printStr
        
        return printStr
  
    def delete_Table(self):
        
        if self.sqlServer.delete_table_name(self.fromUser)==True:
            if self.sqlServer.delete_tableitem('usertablerelation', 'tablename=\'%s\''%self.fromUser)==True:
                return u'注销成功'
            else:
                print u"请管理员注意tablename=%s在usertablerelation表中有残留"%self.fromUser
                return  u'注销成功，但关系表有残留，请联系管理员同学'
        else:
            return u'注销失败,请确认是否注册过；如果注册过，注销失败，请联系管理员同学'
 
    def addUserData(self,msg):
        
        addFlag = False
        
        factorList = msg.split('+')
        
        if len(factorList)!=2:
            return "字符中有多个加号，格式错误"
        elif factorList[1]=='':
            return "没有数值输入"
        else:
            try:
                score = int(factorList[1])
            except:
                return "请在+号后正确输入数字"
            
            try:
                result = self.sqlServer.get_table_value(self.fromUser)
            except:
                return u"请先注册"
            
            result = result[-1]
            
            lastTime = result[1]
            
            if result[-1] == -1:
                currentPoint = 1
                addFlag = True
            else:
                try:
                    currentPoint = int(result[0])
                except:
                    return u"数据错误，请联系管理员"
                    
            currentTime = self.getLocalTime()
            
            if not addFlag and lastTime[:10] != currentTime[:10]:
                currentPoint += 1
                addFlag = True
            
            if addFlag:
                #插入数据
                print "进入插入数据"
                strParam = '(name,scoretime,userscore)'
                strFormat = '(%s,%s,%s)'
            
                valueFormat = [(str(currentPoint),currentTime,score)]
                self.sqlServer.insert_last_data(self.fromUser,strParam,strFormat,valueFormat)
            else:
                #更新数据
                print "进入更新数据"
                strFormat = 'name=' + str(currentPoint)
                strModifyTime = "scoretime=\'%s\'"%str(currentTime)
                strModifyScore = 'userscore=' + str(score)
                self.sqlServer.update_table_value(self.fromUser,strFormat,strModifyTime)
                self.sqlServer.update_table_value(self.fromUser,strFormat,strModifyScore)
   
            return u"数据更新成功，当天总数据以此次提交为准"
    
    def create_and_initTable(self,msg):
        print "kaishizhuce"
        factorList = msg.split('+')
        
        if len(factorList) != 2:
            return "注册格式不正确，请确认名称中没有加号"
        elif factorList[1]!='':
            name = factorList[1]
            
            strParam = '(name char(50) primary key, scoretime char(50), userscore int)'
            flag=self.sqlServer.creat_table_name(self.fromUser,strParam)
            if flag == "you have registered or table is exist":
                
                return u'你曾经注册过，请输入找回注册号找回'
            elif flag ==False:
                return u'注册失败'
            else:
                '''
                #调用类变量存储表名称,SAE对类变量支持不好，此路不通，改用数据库
                message.listTableName.append(self.fromUser)
                print message.listTableName
                 
                '''
                
                 
                strParam = '(name,scoretime,userscore)'
                strParamrela='(tablename,username)'
                strFormat = '(%s,%s,%s)'
                strFormatrela='(%s,%s)'
        
                
                localTime = self.getLocalTime()
                valueFormat = [(name,localTime,-1)]
                valueFormatrela=[(self.fromUser,name)]
                self.sqlServer.insert_last_data(self.fromUser,strParam,strFormat,valueFormat)
                self.sqlServer.insert_last_data('usertablerelation', strParamrela, strFormatrela, valueFormatrela)
                return u'注册成功'
        else:
            return "请确认一下是否填写了注册名称"
        
    
    def recordUserResult(self,msg):
        
        factorList = msg.split('+')
        
        if len(factorList) != 4:
            return msg
        
        (_,pointNum,teamNum,scoreNum) = factorList
        
        if int(pointNum) not in range(1,9) or  int(teamNum) not in range(1,51) or int(scoreNum) not in range(0,101):
            return msg
        
        if int(scoreNum) != 0:
            scoreNum = str(self.perPointScore + int(scoreNum))
        
        retMsg = self.openAndWrite(teamNum, pointNum, scoreNum)
        
        if int(scoreNum) == 0:
            msg = teamNum + u"号小组在第" + pointNum + u"个关卡处的积分删除成功" 
        else:
            msg = teamNum + u"号小组在第" + pointNum + u"个关卡处的积分是：" + scoreNum + retMsg
        
        return msg
    
    def getRecordFromeUser(self,msg):
        
        factorList = msg.split('+')
        
        if len(factorList) != 2:
            return msg
        
        iTeamNum = int(factorList[1])
        
        if iTeamNum not in range(1,self.teamNum+1):
            return msg
        
        teamDict = self.getScoreTeamNum(iTeamNum)
        if len(teamDict) == 0:
            return u"没有查找到该组的成绩"
        
        replyMsg = str(iTeamNum) + u"小组积分：\n------------\n"
        totalScore = 0
        
        for iPointTemp in teamDict.iterkeys():
            iScoreNum = teamDict[iPointTemp]
            
            totalScore += iScoreNum
            replyMsg += u"关卡"+str(iPointTemp)+u"积分：" + str(iScoreNum) + "\n"
            
        replyMsg += u"总积分：" + str(totalScore)
            
        return replyMsg
    
    def getRecordFromePoint(self,msg):
        
        try:
            iPointNum = int(msg[-1])
        except:
            return msg
        
        if iPointNum not in range(1,self.pointNum+1):
            return msg
        
        pointTuple = self.getScorePointNum(iPointNum)
        if len(pointTuple) == 0:
            return u"没有查找到该关卡的成绩"
        
        replyMsg = str(iPointNum) + u"关卡积分：\n------------\n"
        totalTeam = 0
        
        for tempTuple in pointTuple:
            if tempTuple[1] != 0:
                totalTeam += 1
            replyMsg += str(tempTuple[0])+u"组：" + str(tempTuple[1]) + "\n"
            
        replyMsg += str(totalTeam) + u"组通过"
            
        return replyMsg
    
    def getScoreTeamNum(self,teamNum):
        
        #获取服务器数据
        resultDict = self.sqlServer.get_agg_table_value(self.listTableName)
        
        result = {}
        for tempKey in resultDict.iterkeys():
            pointNum = int(tempKey[5:])
            for tempT in resultDict[tempKey]:
                if tempT[0] == teamNum:
                    result[pointNum] = tempT[1]
        return result
    
    def getScorePointNum(self,pointNum):
        
        tableName = self.tableTag + str(pointNum)
        
        #获取服务器数据
        return self.sqlServer.get_table_value(tableName)
    
    def openAndWrite(self, teamNum, pointNum, scoreNum):
        
        tableName = self.tableTag + pointNum
        strFormat = 'team=' + teamNum
        strModify = 'score=' + scoreNum
        
        self.sqlServer.update_table_value(tableName,strFormat,strModify)
        
        return u'\n保存成功'
    '''
    def getRanking(self):
        
        #获取服务器数据
        resultDict = self.sqlServer.get_agg_table_value(self.listTableName)
        
        result = {}
        total1Score = 0
        temp11 = 0
        printStr = u'\n'
        
        for tempResult in resultDict:
            if tempResult[-1] == -1:                
                #result[0] = tempResult[0]
                temp11 = tempResult[0]
                #return 222
            else:
                printStr = tempResult[0] + tempResult[1] + tempResult[2]
                return printStr
                tempScore = tempResult[2]               
                total1Score += tempScore               
                #return 333
                
        #printStr = str(totalScore) + 'km\n'
        
        return 444
        
        for tempKey in resultDict.iterkeys():
            for tempT in resultDict[tempKey]:
                if tempT[2] != 0:
                    temp11 += tempT[2]
                    return temp11
                    if result.get(tempT[0]):
                        return u'没有排名信息1'
                        result[tempT[0]] += tempT[1]
                    else:
                        return tempT[1]
                        result[tempT[0]] = tempT[1]
        if len(result) == 0:
            return u'没有排名信息'
        
        listResult = sorted(result.items(), lambda x, y: cmp(x[1], y[1]),reverse=True)
        effectNum = len(listResult)
        
        dictResult = {}
        #处理积分相同的情况
        point = 0
        for tempIndex in xrange(effectNum):
            if tempIndex < point:
                continue
            tempTuple = listResult[tempIndex]
            tempScore = tempTuple[1]
            tempList = []
            for tempIndex2 in xrange(tempIndex,effectNum):
                tempTuple2 = listResult[tempIndex2]
                if tempTuple2[1] == tempScore:
                    tempList.append(tempTuple2[0])
                else:
                    point = tempIndex2
                    break
            dictResult[tempScore] = sorted(tempList)
            
        #返回结果
        rankNum = 1
        replyMsg = u'名-组--分---奖:\n'
        tempKeys = sorted(dictResult.keys(),reverse=True)
        for tempScoreNum in tempKeys:
            if tempScoreNum >= 4000:
                tempScoreFlag = 7
            elif tempScoreNum >= 3500:
                tempScoreFlag = 3
            else:
                tempScoreFlag = 1
            for tempTeamNum in dictResult[tempScoreNum]:
                 if rankNum <= 5:
                     tempRankFlag = 7
                 elif rankNum <= 20:
                     tempRankFlag = 3
                 else:
                     tempRankFlag = 1
                 if tempScoreFlag&tempRankFlag&4:
                     tempStr = u'1'
                 elif tempScoreFlag&tempRankFlag&2:
                     tempStr = u'2'
                 else:
                     tempStr = u'3'
                 strSep1 = '-'
                 strTempTeamNum = str(tempTeamNum)
                 strSep2 = '-'*(3 - len(strTempTeamNum))
                 strTempScoreNum = str(tempScoreNum)
                 strSep3 = '-'*(5 - len(strTempScoreNum))
                 strRankNum = str(rankNum)
                 replyMsg += ' ' + strRankNum + '--'+strTempTeamNum+strSep2+strTempScoreNum+strSep3+tempStr+'\n'
                 rankNum += 1
        
        replyMsg += u'有效成绩' + str(rankNum-1) + u'组'
        return replyMsg
        
    
    def getRanking1(self):
        
        #获取服务器数据
        resultDict = self.sqlServer.get_agg_table_value(self.listTableName)
        
        result = {}
        for tempKey in resultDict.iterkeys():
            for tempT in resultDict[tempKey]:
                if tempT[1] != 0:
                    if result.get(tempT[0]):
                        result[tempT[0]] += tempT[1]
                    else:
                        result[tempT[0]] = tempT[1]
        if len(result) == 0:
            return u'没有排名信息'
        
        listResult = sorted(result.items(), lambda x, y: cmp(x[1], y[1]),reverse=True)
        effectNum = len(listResult)
        
        dictResult = {}
        #处理积分相同的情况
        point = 0
        for tempIndex in xrange(effectNum):
            if tempIndex < point:
                continue
            tempTuple = listResult[tempIndex]
            tempScore = tempTuple[1]
            tempList = []
            for tempIndex2 in xrange(tempIndex,effectNum):
                tempTuple2 = listResult[tempIndex2]
                if tempTuple2[1] == tempScore:
                    tempList.append(tempTuple2[0])
                else:
                    point = tempIndex2
                    break
            dictResult[tempScore] = sorted(tempList)
            
        #返回结果
        rankNum = 1
        replyMsg = u'名-组--分---奖:\n'
        tempKeys = sorted(dictResult.keys(),reverse=True)
        for tempScoreNum in tempKeys:
            if tempScoreNum >= 4000:
                tempScoreFlag = 7
            elif tempScoreNum >= 3500:
                tempScoreFlag = 3
            else:
                tempScoreFlag = 1
            for tempTeamNum in dictResult[tempScoreNum]:
                 if rankNum <= 5:
                     tempRankFlag = 7
                 elif rankNum <= 20:
                     tempRankFlag = 3
                 else:
                     tempRankFlag = 1
                 if tempScoreFlag&tempRankFlag&4:
                     tempStr = u'1'
                 elif tempScoreFlag&tempRankFlag&2:
                     tempStr = u'2'
                 else:
                     tempStr = u'3'
                 strSep1 = '-'
                 strTempTeamNum = str(tempTeamNum)
                 strSep2 = '-'*(3 - len(strTempTeamNum))
                 strTempScoreNum = str(tempScoreNum)
                 strSep3 = '-'*(5 - len(strTempScoreNum))
                 strRankNum = str(rankNum)
                 replyMsg += ' ' + strRankNum + '--'+strTempTeamNum+strSep2+strTempScoreNum+strSep3+tempStr+'\n'
                 rankNum += 1
        
        replyMsg += u'有效成绩' + str(rankNum-1) + u'组'
        return replyMsg
    '''
    def getRanking(self):
        print "jinru-messageranking"
        userwithtable=self.sqlServer.get_table_value('usertablerelation')
        print userwithtable
        listtablename=[]
        for temp in userwithtable:
            print temp[0]
            listtablename.append(temp[0])
        
        #获取服务器数据
        resultDict = self.sqlServer.get_agg_table_value(listtablename)
        score={}
        print resultDict
        
        for temp in resultDict:
            length=0
            score[temp]=0
            while length<len(resultDict[temp]):
                #print dict[temp][length][2]
                if resultDict[temp][length][2]==-1:
                    score[temp]+=0
                    length+=1
                else:
                    score[temp]+=resultDict[temp][length][2]
                    length+=1
                    
        listResult = sorted(score.items(), lambda x, y: cmp(x[1], y[1]),reverse=True)
        print listResult
        mingci=1
        rankresult=''
        
        for temprank in listResult:
            rankresulttemp=u"第%d名  is %s,the total is %d \n"%(mingci,temprank[0],temprank[1])
            rankresult+=rankresulttemp
            mingci+=1
            
        replyMsg=rankresult
        print replyMsg
        
        return replyMsg
    
    
    def getmonthRanking(self,msg):
        factorList = msg.split('+')
        
        if len(factorList) != 2:
            return "输入格式不正确，请确认输入值合法"
        elif factorList[1].isdigit()==1:
            print "jinru-messagemonthranking"
            print factorList[1]
            factorlisttemp=''
            monthtemp=''
            if len(factorList[1])!=6:
                return u"请确认输入值合法"
            monthtemp+=factorList[1][4]
            monthtemp+=factorList[1][5]
            monthtemp=int(monthtemp)
            print monthtemp
            
            
            if monthtemp<13 and monthtemp>0: 
                for i in range(0,len(factorList[1])):
                    if i==4:
                        factorlisttemp+='-'
                        factorlisttemp+=factorList[1][i] 
                    else:
                        factorlisttemp+=factorList[1][i]
                               
                factorList[1]=factorlisttemp    
                print factorList[1]
                
                
                
                userwithtable=self.sqlServer.get_table_value('usertablerelation')
                print userwithtable
                listtablename=[]
                for temp in userwithtable:
                    print temp[0]
                    listtablename.append(temp[0])
                    
                #获取服务器数据
                resultDict = self.sqlServer.get_agg_table_value(listtablename)
                score={}
                print resultDict
                
                for temp in resultDict:
                    length=0
                    score[temp]=0
                    while length<len(resultDict[temp]):
                        
                        print resultDict[temp][length][1][:7]
                        #注册时候的成绩标记为-1
                        if resultDict[temp][length][2]==-1:
                            score[temp]+=0
                            length+=1
                            
                        elif resultDict[temp][length][1][:7]==factorList[1]:
    
                            score[temp]+=resultDict[temp][length][2]
                            length+=1
                        else:
                            length+=1
                            
                listResult = sorted(score.items(), lambda x, y: cmp(x[1], y[1]),reverse=True)
                print listResult
                mingci=1
                rankresult=''
                
                for temprank in listResult:
                    rankresulttemp=u"第%d名  is %s,the total is %d \n"%(mingci,temprank[0],temprank[1])
                    rankresult+=rankresulttemp
                    mingci+=1
                    
                replyMsg=rankresult
                print replyMsg
                
                return replyMsg
            else:
                return u"请确认输入值合法"
            
            
        else:
            return u"请确认输入值合法"    
                
            
        