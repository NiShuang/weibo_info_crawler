# coding=utf-8

"""  
Created on 2016-04-24 @author: Eastmount

功能: 爬取新浪微博用户的信息及微博评论
网址：http://weibo.cn/ 数据量更小 相对http://weibo.com/

"""    

import time            
import re            
import os    
import sys  
import codecs  
import shutil
import urllib 
from selenium import webdriver        
from selenium.webdriver.common.keys import Keys        
import selenium.webdriver.support.ui as ui        
from selenium.webdriver.common.action_chains import ActionChains



#先调用无界面浏览器PhantomJS或Firefox    
#driver = webdriver.PhantomJS(executable_path="G:\phantomjs-1.9.1-windows\phantomjs.exe")    
driver = webdriver.Firefox()
wait = ui.WebDriverWait(driver,10)


#全局变量 文件操作读写信息
inforead = codecs.open("SinaWeibo_List_best_1.txt", 'r', 'utf-8')
infofile = codecs.open("SinaWeibo_Info_best_1.txt", 'a', 'utf-8')


#********************************************************************************
#                            第一步: 登陆weibo.cn 
#        该方法针对weibo.cn有效(明文形式传输数据) weibo.com见学弟设置POST和Header方法
#                LoginWeibo(username, password) 参数用户名 密码
#********************************************************************************

def LoginWeibo(username, password):
    try:
        #输入用户名/密码登录
        print u'准备登陆Weibo.cn网站...'
        driver.get("http://login.sina.com.cn/")
        elem_user = driver.find_element_by_name("username")
        elem_user.send_keys(username) #用户名
        elem_pwd = driver.find_element_by_name("password")
        elem_pwd.send_keys(password)  #密码
        #elem_rem = driver.find_element_by_name("safe_login")
        #elem_rem.click()             #安全登录

        #重点: 暂停时间输入验证码(http://login.weibo.cn/login/ 手机端需要)
        time.sleep(20)
        
        #elem_sub = driver.find_element_by_xpath("//input[@class='smb_btn']")
        #elem_sub.click()              #点击登陆 因无name属性
        elem_pwd.send_keys(Keys.RETURN)
        time.sleep(2)
        
        #获取Coockie 推荐资料：http://www.cnblogs.com/fnng/p/3269450.html
        print driver.current_url
        print driver.get_cookies()  #获得cookie信息 dict存储
        print u'输出Cookie键值对信息:'
        for cookie in driver.get_cookies(): 
            #print cookie
            for key in cookie:
                print key, cookie[key]
                    
        #driver.get_cookies()类型list 仅包含一个元素cookie类型dict
        print u'登陆成功...'
        
        
    except Exception,e:      
        print "Error: ",e
    finally:    
        print u'End LoginWeibo!\n\n'


#********************************************************************************
#                  第二步: 访问个人页面http://weibo.cn/5824697471并获取信息
#                                VisitPersonPage()
#        编码常见错误 UnicodeEncodeError: 'ascii' codec can't encode characters 
#********************************************************************************

def VisitPersonPage(user_id):

    try:
        global infofile       #全局文件变量
        url = "http://weibo.com/" + user_id
        driver.get(url)
        print u'准备访问个人网站.....', url
        print u'个人详细信息'
        
        #用户id
        print u'用户id: ' + user_id

        #昵称
        str_name = driver.find_element_by_xpath("//div[@class='pf_username']/h1")
        name = str_name.text        #str_name.text是unicode编码类型
        print u'昵称: ', name
        
        #关注数 粉丝数 微博数 <td class='S_line1'>
        str_elem = driver.find_elements_by_xpath("//table[@class='tb_counter']/tbody/tr/td/a")
        str_gz = str_elem[0].text    #关注数
        num_gz = re.findall(r'(\w*[0-9]+)\w*', str_gz)
        str_fs = str_elem[1].text    #粉丝数
        num_fs = re.findall(r'(\w*[0-9]+)\w*', str_fs)
        str_wb = str_elem[2].text    #微博数
        num_wb = re.findall(r'(\w*[0-9]+)\w*', str_wb)
        print u'关注数: ', num_gz[0]
        print u'粉丝数: ', num_fs[0]
        print u'微博数: ', num_wb[0]

        #文件操作写入信息
        infofile.write('=====================================================================\r\n')
        infofile.write(u'用户: ' + user_id + '\r\n')
        infofile.write(u'昵称: ' + name + '\r\n')
        infofile.write(u'关注数: ' + str(num_gz[0]) + '\r\n')
        infofile.write(u'粉丝数: ' + str(num_fs[0]) + '\r\n')
        infofile.write(u'微博数: ' + str(num_wb[0]) + '\r\n')
        
        
    except Exception,e:      
        print "Error: ",e
    finally:    
        print u'VisitPersonPage!\n\n'
        print '**********************************************\n'
        infofile.write('=====================================================================\r\n\r\n')


#********************************************************************************
#                  第三步: 访问http://s.weibo.com/页面搜索热点信息
#                  爬取微博信息及评论，注意评论翻页的效果和微博的数量
#********************************************************************************    

def GetComment(key):
    try:
        global infofile       #全局文件变量
        driver.get("http://s.weibo.com/")
        print u'搜索热点主题：', key

        #输入主题并点击搜索
        item_inp = driver.find_element_by_xpath("//input[@class='searchInp_form']")
        item_inp.send_keys(key)
        item_inp.send_keys(Keys.RETURN)    #采用点击回车直接搜索

        #内容
        #content = driver.find_elements_by_xpath("//div[@class='content clearfix']/div/p")
        content = driver.find_elements_by_xpath("//p[@class='comment_txt']")
        print content
        i = 0
        print u'长度', len(content)
        while i<len(content):
            print '微博信息:'
            print content[i].text
            infofile.write(u'微博信息:\r\n')
            infofile.write(content[i].text + '\r\n')
            i = i + 1

        #评论 由于评论是动态加载，爬取失败
        #Error:  list index out of range
        comment = driver.find_elements_by_xpath("//p[@class='list_ul']/dl/dd/div[0]")
        j = 0
        while j<10:
            print comment[j].text
            j = j + 1


    except Exception,e:      
        print "Error: ",e
    finally:    
        print u'VisitPersonPage!\n\n'
        print '**********************************************\n'

        
        
#*******************************************************************************
#                                程序入口 预先调用
#         注意: 因为sina微博增加了验证码,但是你用Firefox登陆输入验证码
#         直接跳转到明星微博那部分,即: http://weibo.cn/guangxianliuyan
#*******************************************************************************
    
if __name__ == '__main__':

    #定义变量
    username = '15201615157'             #输入你的用户名
    password = '*********'               #输入你的密码

    #操作函数
    LoginWeibo(username, password)       #登陆微博

    #在if __name__ == '__main__':引用全局变量不需要定义 global inforead 省略即可
    print 'Read file:'
    user_id = inforead.readline()
    while user_id!="":
        user_id = user_id.rstrip('\r\n')
        print user_id
        VisitPersonPage(user_id)         #访问个人页面http://weibo.cn/guangxianliuyan
        user_id = inforead.readline()
        #break

    #搜索热点微博 爬取评论
    key = u'欢乐颂' 
    GetComment(key)
    
    infofile.close()
    inforead.close()
    
    

    
