# -*- coding: utf-8 -*-
import win32api,win32con,win32gui
from appium.webdriver.mobilecommand import MobileCommand
from appium import webdriver as appdriver
from selenium import webdriver
from selenium.webdriver import ActionChains
import time,datetime,os
import random
from auto_captcha import *
import MySQLdb

def get_conn():
    conn = MySQLdb.connect(host='192.168.0.97',user='oeasytest',passwd='123456',db='autotest_platform',port=3306,charset='utf8')
    return conn

conn = get_conn()
cur = conn.cursor()

def get_sql_data(sql):
    cur.execute(sql)
    data = cur.fetchall()
    return data

#======================当前时间
now = datetime.datetime.now()
second_delay = datetime.timedelta(seconds=22)   #22秒，刚好公告发布完就生效
present_time = now.strftime("%Y-%m-%d")
present_time1 = now.strftime("%Y-%m-%d %H:%M:%S")
present_time2 = now.strftime("%Y")
present_time2 = int(present_time2) - 1
present_time2 = str(present_time2)
present_time_delay = now + second_delay
present_time_delay = str(present_time_delay)[:19]

#======================获取udid
def get_udid(var1):
    tmp = os.popen('adb devices -l')
    for rec in tmp:
        if(var1 in rec):
            end = rec.find(' ')
            Hol_T00_udid = rec[:end]
            return Hol_T00_udid

#======================启动1号社区app
def start_one():
    app = {}
    app['platformName'] = 'Android'
    app['platformVersion'] = '4.2.2'
    app['deviceName'] = 'Android Emulator'
    app['appPackage'] = 'com.oecommunity.oeshop'
    app['appActivity'] = '.component.intro.activity.WelcomeActivity'
    app['udid'] = get_udid('Hol_T00')
    one_driver = appdriver.Remote('http://localhost:4723/wd/hub', app)
    return one_driver

#======================启动物业+app
def start_plus():
    app = {}
    app['platformName'] = 'Android'
    app['platformVersion'] = '4.2.2'
    app['deviceName'] = 'Android Emulator'
    app['appPackage'] = 'com.oeasy.propertycloud'
    app['appActivity'] = '.ui.activity.WelcomActivity'
    plus_driver = appdriver.Remote('http://localhost:4723/wd/hub', app)
    return plus_driver

#======================启动门口机
def start_intercom():
    app = {}
    app['platformName'] = 'Android'
    app['platformVersion'] = '4.4.2'
    app['deviceName'] = 'Android Emulator'
    app['appPackage'] = 'com.tcl.eshow'
    app['appActivity'] = 'com.tcl.eshow.EShowActivit'
    intercom_driver = appdriver.Remote('http://localhost:4723/wd/hub', app)
    return intercom_driver

#======================切换到h5 context
def switch_h5(var1,var2):
    var1.execute(MobileCommand.SWITCH_TO_CONTEXT, {"name": var2})

#======================清空文本框
def clear_EditText(driver):
    driver.press_keycode(29,28672)
    driver.press_keycode(112)

#======================获取app进程号
def get_oeasy_progress():
    oeasy_progress = os.popen('adb shell ps | find "oeshop"')
    oeasy_progress = oeasy_progress.readlines()
    for rec in oeasy_progress:
        rec = re.split('\s',rec)
        oeasy_progress_no = rec[4]
        print('oeasy 进程号 = ',oeasy_progress_no)

#======================获得机器屏幕大小x,y
def getSize(var1):
    x = var1.get_window_size()['width']
    y = var1.get_window_size()['height']
    return (x, y)

#======================屏幕向上滑动
def swipeUp(var1,t):
    l = getSize(var1)
    x1 = int(l[0] * 0.5)  #x坐标
    y1 = int(l[1] * 0.5)   #起始y坐标
    y2 = int(l[1] * 0.35)   #终点y坐标
    var1.swipe(x1, y1, x1, y2,t)

#======================屏幕向上滑动
def scroll_up(var1,t):
    try:
        swipeUp(var1,t)   ,time.sleep(1)
    except Exception:
        pass

#======================上传图片
def upload_pic(driver):
    win32api.keybd_event(84,0,0,0)  #t
    win32api.keybd_event(84,0,win32con.KEYEVENTF_KEYUP,0) #释放按键
    win32api.keybd_event(69,0,0,0)  #e
    win32api.keybd_event(69,0,win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(83,0,0,0)  #s
    win32api.keybd_event(83,0,win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(84,0,0,0)  #t
    win32api.keybd_event(84,0,win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(110,0,0,0)  #.
    win32api.keybd_event(110,0,win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(74,0,0,0)  #j
    win32api.keybd_event(74,0,win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(80,0,0,0)  #p
    win32api.keybd_event(80,0,win32con.KEYEVENTF_KEYUP,0)
    win32api.keybd_event(71,0,0,0)  #g
    win32api.keybd_event(71,0,win32con.KEYEVENTF_KEYUP,0)
    time.sleep(1)
    #按确定键
    win32api.keybd_event(13,0,0,0)  #enter
    win32api.keybd_event(13,0,win32con.KEYEVENTF_KEYUP,0)   ,wait(driver,0.5)

#======================等待时间
def wait(driver,var1 = 1):
    driver.implicitly_wait(30)
    time.sleep(var1)

#======================iframe
def switch_to_iframe(driver,var1):
    driver.switch_to.frame(driver.find_element_by_xpath("//iframe[contains(@src,'"+var1+"')]"))

#======================移除只读限制
def remove_readonly(driver,var1):
    js = "document.getElementById('"+var1+"').removeAttribute('readonly')"  # 1.原生js，移除属性
    # js = "$('input[id='"+var1+"']').removeAttr('readonly')"  # 2.jQuery，移除属性
    # js = "$('input[id='"+var1+"']').attr('readonly',false)"  # 3.jQuery，设置为false
    # js = "$('input[id='"+var1+"']').attr('readonly','')"  # 4.jQuery，设置为空（同3）
    driver.execute_script(js)

#======================定义driver
def get_driver(ip,url):
    driver = webdriver.Chrome()
    driver.implicitly_wait(30)
    base_url = ip
    driver.maximize_window()
    driver.get(base_url + url)
    return driver

#======================登录物业后台
def log_in_property(driver,username,password):
    print(driver.current_url)
    driver.find_element_by_name("username").clear()
    driver.find_element_by_name("username").send_keys(username)
    driver.find_element_by_name("password").clear()
    driver.find_element_by_name("password").send_keys(password)
    code=get_captcha(driver)
    driver.find_element_by_name("captcha").clear()
    driver.find_element_by_name("captcha").send_keys(code)
    time.sleep(1)
    driver.find_element_by_id("btnSubmit").click()     ,wait(driver,1.5)
    n=0
    #识别5次验证码，如果7次都没识别出来，测试fail
    while(driver.current_url[:42]=="http://192.168.0.96/yihao01-park-sso/login" and n<5):
        driver.find_element_by_name("username").clear()
        driver.find_element_by_name("username").send_keys(username)
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys(password)
        code = get_captcha(driver)
        driver.find_element_by_name("captcha").clear()
        driver.find_element_by_name("captcha").click()
        driver.find_element_by_name('captcha').send_keys(code)
        time.sleep(1)
        driver.find_element_by_id("btnSubmit").click()     ,wait(driver,1.5)
        n += 1
    if n == 5:
        print_log('输入验证码失败')
        return False
    else:
        return True

# #======================登录运营后台
# def log_in_operation(driver,username,password):
#     driver.find_element_by_name("userDTO.userModel.loginName").clear()
#     driver.find_element_by_name("userDTO.userModel.loginName").send_keys(username)
#     driver.find_element_by_name("userDTO.userModel.passwd").clear()
#     driver.find_element_by_name("userDTO.userModel.passwd").send_keys(password)
#     driver.find_element_by_name("kaptcha").click()
#     print_log('请在5秒钟之内输入验证码...')
#     time.sleep(5)
#     driver.find_element_by_id("btnSubmit").click()     ,wait(driver,1.5)

#======================登录运营后台
def log_in_operation(driver,username,password):
    driver.find_element_by_name("userDTO.userModel.loginName").clear()
    driver.find_element_by_name("userDTO.userModel.loginName").send_keys(username)
    driver.find_element_by_name("userDTO.userModel.passwd").clear()
    driver.find_element_by_name("userDTO.userModel.passwd").send_keys(password)
    code=get_captcha(driver)
    driver.find_element_by_name("kaptcha").clear()
    driver.find_element_by_name("kaptcha").send_keys(code)
    time.sleep(1)
    driver.find_element_by_id("btnSubmit").click()     ,wait(driver,1.5)
    n=0
    #识别5次验证码，如果7次都没识别出来，测试fail
    while(driver.current_url=="http://192.168.0.96/comp/login.jsp" and n<5):
        driver.find_element_by_id("kaptchaImage").click()
        driver.find_element_by_name("userDTO.userModel.loginName").clear()
        driver.find_element_by_name("userDTO.userModel.loginName").send_keys(username)
        driver.find_element_by_name("userDTO.userModel.passwd").clear()
        driver.find_element_by_name("userDTO.userModel.passwd").send_keys(password)
        code = get_captcha(driver)
        driver.find_element_by_name("kaptcha").clear()
        driver.find_element_by_name("kaptcha").click()
        driver.find_element_by_name('kaptcha').send_keys(code)
        time.sleep(1)
        driver.find_element_by_id("btnSubmit").click()     ,wait(driver,1.5)
        n += 1
    if n == 5:
        print_log('输入验证码失败')
        return False
    else:
        return True

def log_in_eshop(driver,username,password):
    '''
    电商登录系统_有验证码
    通过URL判定是否登录成功，比判定元素快，如果网速较慢可能会判定失败
    :param driver:
    :param username: 账号
    :param password: 密码
    :return:
    '''
    driver.find_element_by_name("userName").clear()
    driver.find_element_by_name("userName").send_keys(username)
    driver.find_element_by_name("password").clear()
    driver.find_element_by_name("password").send_keys(password)
    code=get_captcha(driver)
    driver.find_element_by_name("kaptcha").clear()
    driver.find_element_by_name('kaptcha').send_keys(code)
    time.sleep(2)
    driver.find_element_by_class_name("loginBt").click() ,wait(driver,2.5)
    n=0
    #识别5次验证码，如果5次都没识别出来，测试fail
    while driver.current_url=='http://192.168.0.96/yihao01-eshop-web/login' and n<5:
        driver.find_element_by_name("userName").clear()
        driver.find_element_by_name("userName").send_keys(username)
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys(password)
        code=get_captcha(driver)
        driver.find_element_by_name("kaptcha").clear()
        driver.find_element_by_name('kaptcha').send_keys(code)
        time.sleep(1)
        driver.find_element_by_class_name("loginBt").click() ,wait(driver,3.5)
        n=n+1
    if n==7:
        print_log('输入验证码失败')
        return False
    else:
        return True

#==切换小区
def swith_village(driver,Select,var1):
    driver.find_element_by_link_text(u"切换小区").click()   ,wait(driver,0.5)
    Select(driver.find_element_by_id("city_select")).select_by_visible_text(u"北京市")     ,wait(driver,0.2)
    Select(driver.find_element_by_id("unit_select")).select_by_visible_text(u""+var1)     ,wait(driver,0.2)
    driver.find_element_by_xpath("//button[@onclick='modalSubmit();']").click()     ,wait(driver,0.5)

#======================打印日志
def print_log(var1,HH = True):
    File = '/autotest_platform/test_out.log'
    File1 = open(File,'a',encoding='utf-8')
    if(HH == ','):
        print(var1,)
        File1.write(var1)
    else:
        print(var1)
        File1.write(str(var1)+'\n')
    File1.close()

#======================生成结果
def generate_result(var1):
    File = 'injection_result.html'
    File1 = open(File,'w',encoding='utf-8')
    File1.truncate()
    print(var1)
    File1.write(var1)
    File1.close()

#======================插入执行成功的用例
def result_insert_sql(var1,var2):
    sql='insert into app1_test_result(case_name,status) values("'+var1+'","'+var2+'")'
    cur.execute(sql)
    conn.commit()


#======================================================================================蒋锦娟
def btnclick(driver,btnname):
    right = driver.find_element_by_class_name('yunTopRight')
    btns = right.find_elements_by_tag_name('a')
    if btnname == u'切换小区':
        btns[0].click()
    else:
        btns[1].click()

###切换小区
def Switch_unit(driver,city,unit):
    btnclick(driver,u'切换小区')
    options = driver.find_element_by_id('city_select').find_elements_by_tag_name('option')
    for option1 in options:
        if option1.text == city:
            #print u'城市 ======' + option1.text
            option1.click()
    units = driver.find_element_by_id('unit_select').find_elements_by_tag_name('option')
    for option2 in units:
        if option2.text == unit:
            #print u'小区名称 ======' + option2.text
            option2.click(),wait(driver,0.5)
    btns = driver.find_element_by_class_name('modal-footer').find_elements_by_tag_name('button')
    btns[0].click(),wait(driver,0.5)
    #for btn in btns:
        #if btn.text == u'确定':
            #print u'按钮名称 ======' + btn.text
            #btn.click(),Methods.wait(driver,0.5)

def Menu_Select2(driver,menu1,menu2,menu3):
    for i in range(10):
        menu_id = 'leftIcon'+str(i)
        menu = driver.find_element_by_id(menu_id)
        if menu.text == menu1:
            menu.click(),wait(driver,0.5)
            break
    dls = driver.find_elements_by_css_selector('div.menu_dropdown.bk_2>dl')
    lis = dls[i].find_elements_by_tag_name('li')
    for li in lis:
        nenu2 = li.find_element_by_tag_name('span')
        if(nenu2.text == menu2 and nenu2.get_attribute('class') != 'on'):
            nenu2.click(),wait(driver,0.5)
        menu3_tags = li.find_elements_by_tag_name('a')
        for menu3_tag in menu3_tags:
            if menu3_tag.text == menu3:
                print()
                menu3_tag.click(),wait(driver,0.5)
                break

#三级目录
def menu3_select(driver,menuname):
    menu3s = driver.find_elements_by_css_selector('div.downnav>a')
    for menu3 in menu3s:
        if menu3.text == menuname:
            menu3.click(),wait(driver,0.5)

#确认框按钮
def btn_click(driver,btnname):
    btn1s = driver.find_elements_by_css_selector('div.xubox_main>span.xubox_botton>a')
    for btn1 in btn1s:
        if btn1.text == btnname:
            btn1.click(),wait(driver,0.5)
            break

#列表界面，查询下拉选择
def select(driver,name):
    options = driver.find_element_by_tag_name('select').find_elements_by_tag_name('option')
    for option in options:
        if option.text == name:
            option.click(),wait(driver,0.5)

def get_buildingname(driver,buildingname):
    options = driver.find_element_by_id('building').find_elements_by_tag_name('option')
    for option in options:
        if option.text == buildingname:
            option.click(),wait(driver,0.5)

#======================================================================================任志爱
def get_current_time(type=0):
    '''
    获取当前时间 created by renzhiai
    windows系统中保存文件，不支持分号‘:’命名，故需要自己调整时间输出格式
    :param type: type=0,时间格式按第一种方式输出，无分号‘：’，type!=0，时间格式按第二种方式输出，有分号‘：’
    :return:返回年月日时分秒，如果月份小于10，月份前面加0
    '''
    #
    if type==0:
        return time.strftime('%Y.%m.%d_%H.%M.%S',time.localtime())
    else:
        return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())

def get_current_time_nozero():
    '''
    获取当前时间 created by renzhiai
    为了匹配电商平台-》商品中心-》分类管理-》修改时间
    :return:返回年月日时分，如果月份小于10，月份前面不需要加0
    '''
    y=str(datetime.datetime.now().year)
    m=str(datetime.datetime.now().month)
    d=str(datetime.datetime.now().day)
    t=str(datetime.datetime.now().time())
    current_time=y+'-'+m+'-'+d+' '+t[0:5]
    return current_time

def get_current_date():
    '''
    获取当前日期
    :return:
    '''
    return str(datetime.datetime.now().date())

def enter_module(driver,modulename,):
    '''
    created by Renzhiai
    点击模块，进入模块
    :param driver:
    :param modulename:模块名字
    :return:
    '''
    modules={'首页':0,'商品中心':1,'营销管理':2,'订单中心':3,'基础管理':4,'内容管理':5}
    if modulename not in modules.keys():
        print(u'modulename错误，请重新输入')
        return False
    driver.find_element_by_css_selector('div[class="nav"]').\
        find_elements_by_tag_name('a')[modules[modulename]].click()   ,wait(driver,2)
    return True

def enter_index(driver,indexname):
    '''
    created by Renzhiai
    点击左边列表
    :param driver:
    :param indexname:左边列表的名字
    :return:
    '''
    if indexname=='商品管理':
        driver.find_elements_by_link_text(indexname)[1].click(),    wait(driver,2)
    else:
        driver.find_element_by_link_text(indexname).click() ,wait(driver,2)
    return True

def randomcode():
    '''
    created by Renzhiai
    :return:
    '''
    letters="qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"
    code=""
    #code=[]
    for i in range(4):
        code+=random.choice(letters)
        #code.append(random.choice(letters))
    return code

def click_add_btn(driver):
    '''
    created by Renzhiai
    :param driver:
    :return:
    '''
    driver.find_element_by_id('addBtn').click()   ,wait(driver)

def click_add_ok_btn(driver):
    '''
    created by Renzhiai
    :param driver:
    :return:
    '''
    driver.find_element_by_id('addOkBtn').click(), wait(driver)

def click_edit_btn(driver):
    '''
    created by Renzhiai
    :param driver:
    :return:
    '''
    driver.find_element_by_id('editBtn').click()   ,wait(driver)

def click_edit_ok_btn(driver):
    '''
    created by Renzhiai
    :param driver:
    :return:
    '''
    driver.find_element_by_id('editOkBtn').click()   ,wait(driver)

def click_delete_btn(driver):
    '''
    created by Renzhiai
    :param driver:
    :return:
    '''
    driver.find_element_by_id('deleteBtn').click()   ,wait(driver)

def click_delete_ok_btn(driver):
    '''
    created by Renzhiai
    :param driver:
    :return:
    '''
    driver.find_element_by_css_selector('a[id=""][group=""]').find_elements_by_tag_name('span')[0].click(), wait(driver)

def send_keys_by_name(driver,name,text):
    '''
    created by Renzhiai
    :param driver:
    :param name:
    :param text:
    :return:
    '''
    driver.find_element_by_name(name).clear()
    driver.find_element_by_name(name).send_keys(text)

def send_keys_by_id(driver,id,text):
    '''
    created by Renzhiai
    :param driver:
    :param id:
    :param text:
    :return:
    '''
    driver.find_element_by_id(id).clear()
    driver.find_element_by_id(id).send_keys(text)

def select_first(driver):
    '''
    created by Renzhiai
    :param driver:
    :return:
    '''
    driver.find_elements_by_css_selector('div[class="datagrid-cell-rownumber"]')[0].click(), wait(driver)

def set_status(driver,status):
    '''
    created by Renzhiai
    设置状态
    :param driver:
    :param status:status给0或者1，0为左边的，可能值是生效、有效，1为右边的，可能的值是失效、无效
    :return:
    '''
    driver.find_elements_by_css_selector('input[type="radio"][name="status"]')[status].click(), wait(driver)

def set_region(driver):
    '''
    created by Renzhiai
    :param driver:
    :return:
    '''
    #选择省份（北京市）
    driver.find_element_by_id('provinceCode').click(), wait(driver)
    driver.find_element_by_id('provinceCode').find_elements_by_tag_name('option')[1].click(), wait(driver)
    #选择市区（北京市）
    driver.find_element_by_id('cityCode').click(), wait(driver)
    driver.find_element_by_id('cityCode').find_elements_by_tag_name('option')[1].click(), wait(driver)
    #选择区县（东城区）
    driver.find_element_by_id('townCode').click(), wait(driver)
    driver.find_element_by_id('townCode').find_elements_by_tag_name('option')[1].click(), wait(driver)
    #点击查询
    driver.find_element_by_id('serachUnits').click(), wait(driver)
    #勾选地区
    driver.find_element_by_name('proSelectAllN').click(), wait(driver)
    #点击添加
    driver.find_element_by_id('addPlotBtn').click(), wait(driver)

def set_period(driver,is_certain=True):
    '''
    created by Renzhiai
    :param driver:
    :param is_certain:
    :return:
    '''
    #设置开始时间
    driver.find_elements_by_css_selector('a[class="textbox-icon combo-arrow"]')[0].click(), wait(driver)
    #选择今天
    driver.find_element_by_link_text(u'今天').click(), wait(driver)
    #设置结束时间
    driver.find_elements_by_css_selector('a[class="textbox-icon combo-arrow"]')[1].click(), wait(driver)
    #点击向右的箭头，增加一年
    driver.find_elements_by_css_selector('div[class="calendar-nav calendar-nextyear"]')[1].click(), wait(driver)
    #点击最后一个日期
    driver.find_elements_by_css_selector('td[class="calendar-day "]')[-1].click(), wait(driver)
    if is_certain==True:
        #点击确定
        driver.find_element_by_link_text('确定').click(), wait(driver)

#======================================================================================李青

#add by liqing 2016-06-09
def generateCarPlate():
    province = u"京津冀晋蒙辽吉黑沪苏浙皖闽赣鲁豫鄂湘粤桂琼渝川贵云藏陕甘青宁新"
    attribution_letter = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    plate_posterior_five = "1234567890ABCDEFGHJKLMNPQRSTUVWXYZ"
    str_province = random.choice(province)
    str_letter = random.choice(attribution_letter)
    #print(str_letter)
    arr_posterior_five = []
    for i in range(5):
        arr_posterior_five.append(random.choice(plate_posterior_five))
    str_posterior_five = ''.join(arr_posterior_five)
    #print str_posterior_five
    #print(str_province+str_letter+str_posterior_five)
    return str_province+str_letter+str_posterior_five

#add by liqing 2016-05-10s
def menuIsShow(driver,span_id):
    classText = driver.find_element_by_id(span_id).get_attribute("class")
    if(classText == ''):
        driver.find_element_by_xpath(".//*[@id="+span_id+"]").click(),wait(driver,1)

#判断元素是否存在  add by liqing 2016-06-01
def isElementExist(driver,element):
    flag=True
    #one_driver = start_one()      ,time.sleep(1)
    try:
        driver.find_element_by_id(element)
        return flag
    except:
        flag=False
        return flag

#判断界面元素是否存在
def is_exist_element(driver,property):
    try:
        driver.find_element_by_id(property)
        return True
    except:
        return False