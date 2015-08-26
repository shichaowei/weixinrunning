# -*- coding: utf-8 -*-
#encoding = utf-8

import sae.const
import MySQLdb
import re

class dbm():
    
    def __init__(self):
        """set init"""
        
    def connect_and_cursor(self):
        self.conn=MySQLdb.connect(host=sae.const.MYSQL_HOST,user=sae.const.MYSQL_USER,passwd=sae.const.MYSQL_PASS,db=sae.const.MYSQL_DB,port=int(sae.const.MYSQL_PORT),charset='utf8')
        self.cur=self.conn.cursor()
        
    def disconnect_and_close(self):
        self.cur.close()
        self.conn.close()
    
    
    #创建单个表格
    def creat_table_name(self,name,strParam):
        
        ret = True
        p=re.compile('Table .* already exists')
        print p
        try:
            self.connect_and_cursor()
            sql = 'create table '+ name + strParam
            self.cur.execute(sql)
            self.conn.commit()
        except Exception,e:
            if p.match(e[1]):
                ret = "you have registered or table is exist"
            else:
                self.disconnect_and_close()
                return False
        finally:
            self.disconnect_and_close()
            
        return ret
		
	# 删除单个表格
    def delete_table_name(self,name):
        
        ret = True
        try:
            
            self.connect_and_cursor()
            sql = 'drop table '+ name
            
            self.cur.execute(sql)
            self.conn.commit()
        except:
            ret = False
        finally:
           self.disconnect_and_close()
            
        return ret
		
    def delete_tableitem(self,tablename,item):
        ret=True
        try:
            self.connect_and_cursor()
            print u"进入删除表项"
            sql='delete from %s where %s'%(tablename,item)
            self.cur.execute(sql)
            self.conn.commit()
        except:
            ret = False
        finally:
           self.disconnect_and_close()
            
        return ret
        
	
    #获取表格中最新的值
    def get_last_data(self,tableName):
        
        try:
            self.connect_and_cursor()
            
            sql = 'select * from ' + tableName
            count = self.cur.execute(sql)
            result = self.cur.fetchone()
            
        finally:
            self.disconnect_and_close()
            return result
            
    #表格插入最新值
    def insert_last_data(self,tableName,strParam,strFormat,valueFormat):
        try:
            self.connect_and_cursor()
            
            sql = 'insert into ' + tableName + strParam + ' values' + strFormat
            self.cur.executemany(sql,valueFormat)
            self.conn.commit()
        finally:
            self.disconnect_and_close()
    
    #批量创建相同格式的表格
    def creat_table_nameList(self,listTableName,strParam):
        try:
            self.connect_and_cursor()
            
            for tempTableName in listTableName:
                sql = 'create table if not exists '+ tempTableName + strParam
                self.cur.execute(sql)
            self.conn.commit()
        finally:
            self.disconnect_and_close()
            
    #初始化所有的表格
    def init_table_nameList(self,listTableName,strParam,strFormat,valueFormat):
        try:
            self.connect_and_cursor()
            
            for tempTableName in listTableName:
                sql = 'insert into ' + tempTableName + strParam + ' values' + strFormat
                self.cur.executemany(sql,valueFormat)
            self.conn.commit()
        finally:
            self.disconnect_and_close()
        
        
    #修改特定表格特定的值
    def update_table_value(self,tableName,strFormat,strModify):
        try:
            print u'进入修改表格参数dbm'
            self.connect_and_cursor()
            
            sql = 'update ' + tableName + ' set ' + strModify + ' where ' + strFormat
            print sql
            self.cur.execute(sql)
            self.conn.commit()
        finally:
            print u'开始关闭update-dbm'
            self.disconnect_and_close()
    
    #获取特定表格的值
    def get_table_value(self,tableName):

        try:
            self.connect_and_cursor()
            
            sql = 'select * from ' + tableName
            count = self.cur.execute(sql)
            result = self.cur.fetchall()
        finally:
            self.disconnect_and_close()
            return result
            
    #获取批量表格的值
    def get_agg_table_value(self,listTableName):
        print listTableName
        result = {}
        try:
            self.connect_and_cursor()
            for tempTableName in listTableName:
                print tempTableName
                sql = 'select * from ' + tempTableName
                self.cur.execute(sql)
                #绝对位置为0的不含成绩，是注册时候写入的一个成绩为-1的值
                self.cur.scroll(0,'absolute')
                resulttemp=self.cur.fetchall()
                for temp in resulttemp:
                    if temp[-1] == -1:
                        userName = temp[0] 
                result[userName] = resulttemp
                print resulttemp
        finally:
            self.disconnect_and_close()
            return result