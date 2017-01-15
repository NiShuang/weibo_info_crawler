# coding=utf-8

"""  
Created on 2016-01-09 @author: Eastmount

功能: 爬取新浪微博用户的信息
信息：用户ID 用户名 注册时间 性别 地址(城市) 是否认证 用户标签(明星、搞笑等信息)
    个人资料完成度 粉丝数 关注数 微博数 粉丝ID列表 关注人ID列表 特别关注列表
网址：http://weibo.cn/ 数据量更小 相对http://weibo.com/

参考：佳琪学弟和datahref博客 使用Selenium获取登录新浪微博的Cookie
java链接：http://datahref.com/book/article.php?article=webcollector_WeiboCrawler 
python：http://blog.csdn.net/warrior_zhang/article/details/50198699
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
inforead = codecs.open("SinaWeibo_List_1.txt", 'r', 'utf-8')
infofile = codecs.open("SinaWeibo_Info_1.txt", 'a', 'utf-8')


#********************************************************************************
#                  第一步: 登陆weibo.cn 获取新浪微博的cookie
#        该方法针对weibo.cn有效(明文形式传输数据) weibo.com见学弟设置POST和Header方法
#                LoginWeibo(username, password) 参数用户名 密码
#********************************************************************************

# 参考：http://download.csdn.net/download/mengh2016/7752097
# 不会出现WebDriverException: Message: 'Can\'t load the profile: 的Firefox＆selenium python版本

def LoginWeibo(username, password):
    try:
        #**********************************************************************
        # 直接访问driver.get("http://weibo.cn/5824697471")会跳转到登陆页面 用户id
        #
        # 用户名<input name="mobile" size="30" value="" type="text"></input>
        # 密码 "password_4903" 中数字会变动,故采用绝对路径方法,否则不能定位到元素
        #
        # 勾选记住登录状态check默认是保留 故注释掉该代码 不保留Cookie 则'expiry'=None
        #**********************************************************************
        
        #输入用户名/密码登录
        print u'准备登陆Weibo.cn网站...'
        driver.get("http://login.weibo.cn/login/")
        elem_user = driver.find_element_by_name("mobile")
        elem_user.send_keys(username) #用户名
        elem_pwd = driver.find_element_by_xpath("/html/body/div[2]/form/div/input[2]")
        elem_pwd.send_keys(password)  #密码
        #elem_rem = driver.find_element_by_name("remember")
        #elem_rem.click()             #记住登录状态
        time.sleep(20)
        elem_sub = driver.find_element_by_name("submit")
        elem_sub.click()              #点击登陆
        time.sleep(2)
        
        #获取Coockie 推荐 http://www.cnblogs.com/fnng/p/3269450.html
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
        global infofile
        print u'准备访问个人网站.....'
        driver.get("http://weibo.cn/" + user_id)

        #**************************************************************************
        # No.1 直接获取 用户昵称 微博数 关注数 粉丝数
        #      str_name.text是unicode编码类型
        #**************************************************************************

        #用户id
        print u'个人详细信息'
        print '**********************************************'
        print u'用户id: ' + user_id

        #昵称
        str_name = driver.find_element_by_xpath("//div[@class='ut']")
        str_t = str_name.text.split(" ")
        num_name = str_t[0]      #空格分隔 获取第一个值 "Eastmount 详细资料 设置 新手区"
        print u'昵称: ' + num_name 

        #微博数 除个人主页 它默认直接显示微博数 无超链接
        str_wb = driver.find_element_by_xpath("//div[@class='tip2']")  
        pattern = r"\d+\.?\d*"   #正则提取"微博[0]" 但r"(\[.*?\])"总含[] 
        guid = re.findall(pattern, str_wb.text, re.S|re.M)
        print str_wb.text        #微博[294] 关注[351] 粉丝[294] 分组[1] @他的
        for value in guid:
            num_wb = int(value)
            break
        print u'微博数: ' + str(num_wb)


        #关注数
        str_gz = driver.find_element_by_xpath("//div[@class='tip2']/a[1]")
        guid = re.findall(pattern, str_gz.text, re.M)
        num_gz = int(guid[0])
        print u'关注数: ' + str(num_gz)

        #粉丝数
        str_fs = driver.find_element_by_xpath("//div[@class='tip2']/a[2]")
        guid = re.findall(pattern, str_fs.text, re.M)
        num_fs = int(guid[0])
        print u'粉丝数: ' + str(num_fs)


        #***************************************************************************
        # N0.2 点击详细资料 在获取用户基本信息 性别 地址 生日 标签
        #      获取属性方法[重点] get_attribute("href") 或者url+id+info/..
        #      在No.1调用方法就可以获取url 我主要感觉这样排版更易懂直观才放在No.2
        #***************************************************************************

        #详细资料url http://weibo.cn/5824697471/info
        print '\n获取相关URL：'
        info = driver.find_element_by_xpath("//div[@class='ut']/a[2]")  #资料 个人[详细资料]
        url_info = info.get_attribute("href")

        #微博url http://weibo.cn/5824697471/profile
        #由于除个人主页外微博默认为显示 <span class="tc">微博[294]</span> 故显示获取url
        #info = driver.find_element_by_xpath("//div[@class='tip2']/a[1]")
        #url_wb = info.get_attribute("href")
        url_wb = "http://weibo.cn/" + user_id + "/profile"

        #关注url http://weibo.cn/5824697471/follow
        info = driver.find_element_by_xpath("//div[@class='tip2']/a[1]")
        url_gz = info.get_attribute("href")

        #粉丝url http://weibo.cn/5824697471/fans
        info = driver.find_element_by_xpath("//div[@class='tip2']/a[2]")
        url_fs = info.get_attribute("href")

        #输出url
        print url_info
        print url_wb
        print url_gz
        print url_fs


        #***************************************************************************
        # No.3 文件操作写入信息
        #***************************************************************************

        infofile.write('=====================================================================\r\n')
        infofile.write(user_id + ' ' + num_name + ' ' + str(num_wb) + ' ' + str(num_gz) + ' ' + str(num_fs) + '\r\n')
        

        #获取个人信息 绝对路径 全是div[@class='c']
        print '\n个人资料信息:'
        #driver.get("http://weibo.cn/" + user_id +"/info")
        driver.get(url_info)
        info = driver.find_element_by_xpath("/html/body/div[5]")  #通常为第5个 如果弹出私信则为第6个
        content = info.text
        print info.text                                           #基本信息 unicode编码
        #content.replace('\n',' ')

        #注意:txt中显示在一行 SubText打开明显分行 但是分别使用下面三个语句后返现是'\n'分割
        '''
        print 'test1'
        print content.split("\n")
        print 'test2'
        print content.split("\r")
        print 'test3'
        print content.split("\r\n")
        '''
        for value in content.split("\n"):
            print value
            infofile.write(value + ';')  #以前是空格分隔
        infofile.write(value + '\r\n')
        
        '''
        #昵称:柳岩 性别:女 地区:北京 获取值:分割
        flog = False
        key = ""
        for value in content.split(":"):
            if flog==False:       #"昵称"为False 跳过
                flog = True
                key = value
                print 'tiaoguo'
                continue
            else:
                flog = False
                #print value       #unicode编码
                print '[' + key + ']' + value
                infofile.write('[' + key + ']' + value + ' ')
        '''
        print '**********************************************'

        

        #***************************************************************************
        # No.4 获取关注人列表
        #***************************************************************************

        #跳页按钮省略
        #由于很多网站采用page连接方便我们爬取 就不再自动化调用浏览器翻页
        #http://weibo.cn/2778357077/follow?page=3
        
        #获取页码
        #报错 Error:  'list' object has no attribute 'text' 因使用find_elements_by 而调用.text
        print u'\n关注人列表信息:' 
        driver.get(url_gz)
        info = driver.find_element_by_xpath("//div[@id='pagelist']/form/div")
        #print info.text            #下页  1/20页
        pattern = r"\d+\.?\d*"     #获取第二个数字 
        guid = re.findall(pattern, info.text, re.S|re.M)
        num_page = int(guid[1])
        #print 'Page: ', num_page
        print '**********************************************'


        #文件写入关注列表人id
        #listfile = codecs.open("SinaWeibo_List.txt", 'w', 'utf-8')
        

        #获取关注人列表
        i = 1
        count = 0
        gz_nums = []
        gz_urls = []
        while i <= num_page:
            url = url_gz + '?page=' + str(i)
            #print url
            driver.get(url)
            info = driver.find_elements_by_xpath("/html/body/table/tbody/tr/td[2]/a[1]")
            for value in info:
                count += 1 
                gz_nums.append(value.text)
                infofile.write(value.text + ' ')
                #print value.text
                url = value.get_attribute("href")
                gz_urls.append(url)
                url_id = url.split("/")[-1]    #获取url最后一个/后的值
                #infofile.write(url + ' ')
                #listfile.write(url_id + '\r\n')
                #print url_id
            #增1
            i = i + 1 
        print u'SUM: ' + str(count)  
        infofile.write('\r\n')
        print '**********************************************'
        
        

        #***************************************************************************
        # No.5 获取粉丝列表
        #***************************************************************************

        print u'\n粉丝列表信息:'
        driver.get(url_fs)
        info = driver.find_element_by_xpath("//div[@id='pagelist']/form/div")
        #print info.text            #下页  1/20页
        pattern = r"\d+\.?\d*"     #获取第二个数字 
        guid = re.findall(pattern, info.text, re.S|re.M)
        num_page = int(guid[1])
        #print 'Page: ', num_page

        fensi_ids = []   #存储粉丝id
        fensi_url = []   #存储粉丝url
        i = 1
        count = 0
        while i <= num_page:
            url = url_fs + '?page=' + str(i)
            #print url
            driver.get(url)
            info = driver.find_elements_by_xpath("//div[@class='c']/table/tbody/tr/td[2]/a[1]")
            for value in info:
                cont = value.text
                #print cont
                infofile.write(cont + ' ')
                fensi_ids.append(cont)
                url = value.get_attribute("href")
                #print url
                fensi_url.append(url)
                count += 1
                #调用函数访问页面
            #增1
            i = i + 1
        print u'SUM: ' + str(count)
        infofile.write('\r\n')
        
        
        
    except Exception,e:      
        print "Error: ",e
    finally:    
        print u'VisitPersonPage!\n\n'
        print '**********************************************\n'
        

    
#*******************************************************************************
#                                程序入口 预先调用
#*******************************************************************************
    
if __name__ == '__main__':

    #定义变量
    username = '1520161****'            #输入你的用户名
    password = '00000000'              #输入你的密码
    
    #user_id = '2778357077'             #用户id url+id访问个人
    #user_id = 'renzhiqiang'
    #user_id = 'guangxianliuyan'  #柳岩
    #'renzhiqiang' 任志强


    #操作函数
    infofile.write(u'用户ID 用户名 微博数 关注数 粉丝数 基本信息 关注人ID列表 粉丝ID列表\r\n\r\n')
    LoginWeibo(username, password)      #登陆微博
    
    

    #SyntaxWarning: name 'inforead' is assigned to before global declaration
    #参考:stackoverflow
    #在if __name__ == '__main__':引用全局变量不需要定义 global inforead 省略即可
    print 'Read file:'
    user_id = inforead.readline()
    while user_id!="":
        user_id = user_id.rstrip('\r\n')
        VisitPersonPage(user_id)         #访问个人页面
        user_id = inforead.readline()
    
    infofile.close()
    inforead.close()
    
    

    
