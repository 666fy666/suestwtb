import base64
import datetime
import json
import os
import random
import re
import smtplib
import sys
import time
import urllib
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import cv2
import requests
from aip import AipOcr
from requests_toolbelt import MultipartEncoder
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from wrapt_timeout_decorator import timeout


def userinfo():
    # 主程序对所有账号进行填报
    with open("acc.txt", 'r+', encoding='utf-8') as f_acc:
        acc_ar = f_acc.read().splitlines()
    print("正在读取账号信息")
    d = str(len(acc_ar))
    time.sleep(3)
    print("读取完毕，本次一共将进行%s个账号填报" % d)
    print("=" * 80)
    check = 0
    fail_acc = []
    start = time.perf_counter()
    driver = Chrome(options=opt)  # 创建Chrome无界面对象
    for i in range(len(acc_ar)):
        total = acc_ar[i]
        accounts, pwd, qq = ret(total)
        for z in range(1, 6):
            try:
                if z == 5:
                    check = check + 1
                    fail_acc.append(accounts)
                    print("学校网站可能崩溃或填报网页api被修改，请联系开发者或者过一段时间重试！！")
                    break
                over = main(driver, accounts, pwd, qq)
                if over == "1":
                    if len(pushplus) > 10:
                        try:
                            data, now = mytime()
                            title = '{}{}健康填报结果'.format(data, now)
                            content = "00:00-03:00为系统维护时间，暂时无法进行健康填报。" + "\n👇👇👇您の本次配置信息如下:👇👇👇\n" + str(
                                config)
                            push_plus(title, content)
                        except Exception as e:
                            print("报错：%s" % e)
                            print("pushplus服务异常，主程序已完成运行")
                    return
                break
            except Exception as e:
                print("报错：%s" % e)
                print("即将重试，请稍后.....\n")
                try:
                    js = "window.open('{}','_blank');"
                    driver.execute_script(js.format('https://webvpn.sues.edu.cn'))
                    driver.switch_to.window(driver.window_handles[-1])
                    driver.maximize_window()
                    mouse = driver.find_element(By.XPATH, '/html/body/div/div/div/header/div/div[2]')
                    ActionChains(driver).move_to_element(mouse).perform()
                    time.sleep(1)
                    driver.find_element(By.XPATH, '/html/body/div/div/div/header/div/div[2]/ul/li[2]/a').click()
                except:
                    pass
                driver.set_window_size(950, 1035)
                all_windows = driver.window_handles
                if len(all_windows) > 1:
                    for j in range(len(all_windows) - 1):
                        try:
                            js = "window.close()"
                            driver.execute_script(js)
                            driver.switch_to.window(driver.window_handles[-1])
                        except:
                            pass
        print("=" * 80)
    end = time.perf_counter()
    alltime = round(end - start)
    driver.quit()
    ms1 = "本次共{}个账号填报结果已全部推送，共用时{}分钟。\n".format(d, round(alltime / 60, 2))
    data, now = mytime()
    title = '{}{}健康填报结果'.format(data, now)
    ms2 = "成功{}个账号，失败{}个账号\n".format(len(acc_ar) - check, check)
    ms3 = "\n".join(fail_acc)
    content = ms1 + ms2 + ms3 + "\n👇👇👇您の本次配置信息如下:👇👇👇\n" + str(config)
    content1 = ms1 + ms2 + ms3
    print(content1)
    if len(pushplus) > 10:
        try:
            push_plus(title, content)
        except Exception as e:
            print("报错：%s" % e)
            print("pushplus服务异常，主程序已完成运行")


def main(driver, accounts, pwd, qq):  # 对单个账号操作
    if email:
        if admin:
            qq = adminemail
        print("账号：【{}】，密码：【{}】，邮箱：【{}@qq.com】".format(accounts, pwd, qq))
    else:
        print("账号：【{}】，密码：【{}】".format(accounts, pwd))
    js = "window.open('{}','_blank');"
    driver.execute_script(js.format('https://webvpn.sues.edu.cn'))
    driver.switch_to.window(driver.window_handles[-1])  # 切换到最新页面
    time.sleep(2)
    driver.find_element_by_xpath("//*[@id='username']").send_keys(accounts)
    driver.find_element_by_xpath("//*[@id='password']").send_keys(pwd)
    digit = driver.find_element_by_xpath("//*[@id='fm1']/div[4]/img")
    digit.screenshot("digit-%s.png" % accounts)
    res = img_to_str("digit-%s.png" % accounts)
    driver.find_element_by_xpath("//*[@id='authcode']").send_keys(str(res))
    driver.find_element_by_xpath("//*[@id='passbutton']").click()
    os.remove("digit-%s.png" % accounts)
    time.sleep(3)
    driver.find_element_by_xpath(
        "//*[@id='__layout']/div/div/div[3]/div/div[2]/div/div[1]/div/div[1]/div/div[1]/a/div[2]/h2").click()
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])  # 切换到最新页面
    print("该账号登陆成功✔")
    time.sleep(2)
    try:
        over = driver.find_element_by_xpath("//*[@id='layui-layer100001']/div[2]").text
        print(over)
        over = "1"
        return over
    except:
        pass
    school = driver.find_element_by_xpath("//*[@id='jtdzinput']/input")
    value = school.get_attribute('value')
    name = driver.find_element_by_xpath("//*[@id='form']/div[6]/div[1]/div/div[2]/div/div/span")
    who = str(name.text)
    address = driver.find_element_by_xpath("//*[@id='jtdzItem']/div[3]/span")
    address = str(address.text)
    address1 = driver.find_element_by_xpath("//*[@id='jtdzItem']/div[1]/span")
    address1 = str(address1.text)
    address2 = driver.find_element_by_xpath("//*[@id='jtdzItem']/div[2]/span")
    address2 = str(address2.text)
    if "三期" in str(value) or "四期" in str(value) or "3期" in str(value) \
            or "4期" in str(value) or "工程技术" in str(value):
        driver.find_element_by_xpath('//*[@id="form"]/div[10]/div/div/div[2]/div/div/label[1]/div/ins').click()  # 在校
        driver.find_element_by_xpath('//*[@id="form"]/div[11]/div/div/div[2]/div/div/label[1]').click()  # 松江校区
        driver.find_element_by_xpath("//*[@id='ssl']/input").send_keys(str(value))
        driver.find_element_by_xpath("//*[@id='qs']/input").send_keys(str(value))
        driver.find_element_by_xpath('//*[@id="form"]/div[19]/div/div/div[2]/div/div/label[1]').click()  # 健康
        value = value + "(在校内)"
    else:
        driver.find_element_by_xpath('//*[@id="form"]/div[10]/div/div/div[2]/div/div/label[2]/div/ins').click()  # 不在校
        driver.find_element_by_xpath('//*[@id="form"]/div[18]/div/div/div[2]/div/div/label[1]/div/ins').click()  # 无风险地区
        driver.find_element_by_xpath('//*[@id="form"]/div[19]/div/div/div[2]/div/div/label[1]/div/ins').click()  # 健康
        value = value + "(不在校)"
    if address1 == address2:
        print("姓名：【{}】,位置：【{}】".format(who, address2 + address + value))
    else:
        print("姓名：【{}】,位置：【{}】".format(who, address1 + address2 + address + value))
    driver.find_element_by_xpath('//*[@id="post"]').click()
    try:
        error = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div[3]')
        error.click()
    except:
        time.sleep(2)
        background = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[1]/img[1]').get_attribute(
            'src')
        img1 = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[1]/img[2]').get_attribute('src')
        img1 = img1.split(',')
        background = background.split(',')
        i = base64.b64decode(img1[1])
        b = base64.b64decode(background[1])
        with open('img-%s.png' % accounts, 'wb+') as d:  # 保存验证码图片
            d.write(i)
        with open('background-%s.png' % pwd, 'wb+') as d:  # 保存验证码图片
            d.write(b)
        bg_img = cv2.imread('background-%s.png' % pwd)  # 背景图片
        tp_img = cv2.imread('img-%s.png' % accounts)  # 缺口图片
        bg_edge = cv2.Canny(bg_img, 100, 200)
        tp_edge = cv2.Canny(tp_img, 100, 200)
        bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
        tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
        res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        th, tw = tp_pic.shape[:2]
        tl = max_loc
        result = (tl[0] + tw / 2, tl[1] + th / 2)
        os.remove('img-%s.png' % accounts)
        os.remove('background-%s.png' % pwd)
        slide_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[2]/div[2]')
        act = ActionChains(driver).drag_and_drop_by_offset(slide_btn, xoffset=result[0] - 27, yoffset=0)
        act.perform()
        act.release()
        for u in range(1, 99):  # 设置有99次的重试机会
            try:
                driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
                time.sleep(2)
                driver.save_screenshot('log/%s.png' % accounts)
                driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/a').click()
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[-1])
                driver.maximize_window()
                mouse = driver.find_element(By.XPATH, '/html/body/div/div/div/header/div/div[2]')
                ActionChains(driver).move_to_element(mouse).perform()
                time.sleep(1)
                driver.find_element(By.XPATH, '/html/body/div/div/div/header/div/div[2]/ul/li[2]/a').click()
                driver.set_window_size(950, 1035)
                js = 'window.close()'
                driver.execute_script(js)
                driver.switch_to.window(driver.window_handles[-1])
                print("第%s次滑动时成功✔" % u)
                break
            except Exception as e:
                print("第%s次滑动时失败，正在重试" % u)
                try:
                    error = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div[3]')
                    error.click()
                except Exception as e:
                    time.sleep(2)
                    background = driver.find_element(By.XPATH,
                                                     '/html/body/div[3]/div/div/div/div[1]/img[1]').get_attribute(
                        'src')
                    img1 = driver.find_element(By.XPATH,
                                               '/html/body/div[3]/div/div/div/div[1]/img[2]').get_attribute(
                        'src')
                    img1 = img1.split(',')
                    background = background.split(',')
                    i = base64.b64decode(img1[1])
                    b = base64.b64decode(background[1])
                    with open('img-%s.png' % accounts, 'wb+') as d:  # 保存验证码图片
                        d.write(i)
                    with open('background-%s.png' % pwd, 'wb+') as d:  # 保存验证码图片
                        d.write(b)
                    bg_img = cv2.imread('background-%s.png' % pwd)  # 背景图片
                    tp_img = cv2.imread('img-%s.png' % accounts)  # 缺口图片
                    bg_edge = cv2.Canny(bg_img, 100, 200)
                    tp_edge = cv2.Canny(tp_img, 100, 200)
                    bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
                    tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
                    res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                    th, tw = tp_pic.shape[:2]
                    tl = max_loc
                    result = (tl[0] + tw / 2, tl[1] + th / 2)
                    os.remove('img-%s.png' % accounts)
                    os.remove('background-%s.png' % pwd)
                    slide_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[2]/div[2]')
                    act = ActionChains(driver).drag_and_drop_by_offset(slide_btn, xoffset=result[0] - 27, yoffset=0)
                    act.perform()
                    act.release()
        if email:
            try:
                push(accounts, qq, who, address, address1, address2)
            except Exception as e:
                print("报错：%s" % e)
                print("邮箱推送时出现错误，主程序已经运行完成")
        else:
            print("未配置邮箱推送服务")
        print("账号：%s,填报成功✔" % accounts)


def mytime():
    data = time.strftime('%m月%d日', time.localtime(time.time()))
    mytime1 = time.localtime()
    if mytime1.tm_hour < 12:
        now = "上午"
    else:
        now = "下午"
    return data, now


def ret(total):
    allin = re.split(r'[:：]', total)
    accounts = re.search(r'\w+', allin[0])
    accounts = accounts.group()
    pwd = allin[1]
    try:
        qq = allin[2]
        if qq == "":
            print("个人邮箱填写不正确，已配置为开发者邮箱")
            qq = adminemail
    except:
        print("个人邮箱填写不正确，已配置为开发者邮箱")
        qq = adminemail
    # print("账号：【{}】，密码：【{}】，邮箱：【{}@qq.com】".format(accounts, pwd, qq))
    return accounts, pwd, qq


def push(accounts, qq, who, address, address1, address2):
    data, now = mytime()
    ms1 = "\n"
    if tips:
        try:
            data, now = mytime()
            if who == "冯宇" or who == "叶文婕":
                timenow, count_down = get_time()
                ms1 = ms1 + "距离2023考研还有%s天\n" % str(count_down)
            else:
                pass
            # print("************在线获取语言库************")
            if now == "上午":
                response = urllib.request.urlopen(
                    "https://gitcode.net/qq_35720175/tip/-/raw/master/am.txt")
                Text = response.readlines()
                am = random.randint(0, len(Text) - 1)
                Text = (Text[am].decode("UTF-8"))
                # print(Text.strip())
                tip = Text.strip()
            elif now == "下午":
                response = urllib.request.urlopen(
                    "https://gitcode.net/qq_35720175/tip/-/raw/master/pm.txt")
                Text = response.readlines()
                pm = random.randint(0, len(Text) - 1)
                Text = (Text[pm].decode("UTF-8"))
                # print(Text.strip())
                tip = Text.strip()
            else:
                response = urllib.request.urlopen(
                    "https://gitcode.net/qq_35720175/tip/-/raw/master/pm.txt")
                Text = response.readlines()
                pm = random.randint(0, len(Text) - 1)
                Text = (Text[pm].decode("UTF-8"))
                # print(Text.strip())
                tip = Text.strip()
            # print("************已联网获取成功************")
            ms1 = ms1 + ('Tips：%s(๑•̀ㅂ•́)و✧\n' % tip)
        except Exception as e:
            print("在线获取语言库失败，报错：%s(该报错不影响主程序运行)" % e)
    if weather:
        try:
            key = 'f4b02e3de1034876ac83b188e8b553f9'
            ID = getID(address, key)
            ms1 = ms1 + getData(address, address1, address2, ID, key) + "\n"
        except Exception as e:
            print("获取天气模块失败，报错：%s(该报错不影响主程序运行)" % e)
    if accounts == "101319132":
        if admin:
            print("您正在使用开发者模式！！！")
        else:
            qy = qywx(1)
            # 发送图片消息, 需先上传至临时素材
            media_id = qy.post_file(r'log/', "%s.png" % accounts)
            ms2 = '{}，您好!\n{}{}健康填报成功\n'.format(who, data, now)
            ms = ms2 + ms1
            qy.send_img(media_id, ['rememberme'])
            qy.send_text(str(ms), ['rememberme'])  # 发送文本消息
    elif accounts == "101319232":
        if admin:
            print("您正在使用开发者模式！！！")
        else:
            qy = qywx(1)
            # 发送图片消息, 需先上传至临时素材
            media_id = qy.post_file(r'log/', "%s.png" % accounts)
            ms2 = '{}，您好!\n{}{}健康填报成功\n'.format(who, data, now)
            ms = ms2 + ms1
            qy.send_img(media_id, ['DaBoq'])
            qy.send_text(str(ms), ['DaBoq'])  # 发送文本消息
    elif accounts == "101319310":
        if admin:
            print("您正在使用开发者模式！！！")
        else:
            qy = qywx(1)
            # 发送图片消息, 需先上传至临时素材
            media_id = qy.post_file(r'log/', "%s.png" % accounts)
            ms2 = '{}，您好!\n{}{}健康填报成功\n'.format(who, data, now)
            ms = ms2 + ms1
            qy.send_img(media_id, ['thenorth'])
            qy.send_text(str(ms), ['thenorth'])  # 发送文本消息
    elif accounts == "101319104":
        qy = qywx(1)
        # 发送图片消息, 需先上传至临时素材
        media_id = qy.post_file(r'log/', "%s.png" % accounts)
        ms2 = '{}，您好!\n{}{}健康填报成功\n'.format(who, data, now)
        ms = ms2 + ms1
        print("您正在使用开发者模式！！！")
        qy.send_img(media_id, ['FengYu'])
        qy.send_text(str(ms), ['FengYu'])
    else:
        try:
            from_addr = 'fy16601750698@163.com'
            password = 'VBRCNCUMSJBAVYQZ'
            # 收信方邮箱
            to_addr = '%s@qq.com' % qq
            # 发信服务器
            smtp_server = 'smtp.163.com'
            msg = MIMEMultipart()
            # 添加附件
            imageFile = 'log/%s.png' % accounts
            imageApart = MIMEImage(open(imageFile, 'rb').read(), imageFile.split('.')[-1])
            imageApart.add_header('Content-Disposition', 'attachment', filename=imageFile)
            msg.attach(imageApart)
            # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
            content = str(ms1)
            textApart = MIMEText(content)
            msg.attach(textApart)
            # 邮件头信息
            msg['From'] = Header(from_addr)
            msg['To'] = Header(to_addr)
            msg['Subject'] = Header('{}，您好！{}{}健康填报成功'.format(who, data, now))
            # 开启发信服务，这里使用的是加密传输
            server = smtplib.SMTP_SSL(smtp_server)
            server.connect(smtp_server, 465)
            # 登录发信邮箱
            server.login(from_addr, password)
            # 发送邮件
            server.sendmail(from_addr, to_addr, msg.as_string())
            server.quit()
            print("本次填报结果已成功推送至：%s@qq.com✔" % qq)
        except:
            from_addr = '657769008@qq.com'
            password = 'dmzcadmcrppdbbcj'
            # 收信方邮箱
            to_addr = '%s@qq.com' % qq
            # 发信服务器
            smtp_server = 'smtp.qq.com'
            # 读取txt
            msg = MIMEMultipart()
            # 添加附件
            imageFile = 'log/%s.png' % accounts
            imageApart = MIMEImage(open(imageFile, 'rb').read(), imageFile.split('.')[-1])
            imageApart.add_header('Content-Disposition', 'attachment', filename=imageFile)
            msg.attach(imageApart)
            # 邮箱正文内容，第一个参数为内容，第二个参数为格式(plain 为纯文本)，第三个参数为编码
            content = str(ms1)
            textApart = MIMEText(content)
            msg.attach(textApart)
            # 邮件头信息
            msg['From'] = Header(from_addr)
            msg['To'] = Header(to_addr)
            msg['Subject'] = Header('{}，您好！{}{}健康填报成功'.format(who, data, now))
            # 开启发信服务，这里使用的是加密传输
            server = smtplib.SMTP_SSL(smtp_server)
            server.connect(smtp_server, 465)
            # 登录发信邮箱
            server.login(from_addr, password)
            # 发送邮件
            server.sendmail(from_addr, to_addr, msg.as_string())
            server.quit()
            print("本次填报结果已成功推送至：%s@qq.com✔" % qq)


def push_plus(title, content):
    token = pushplus  # 在pushpush网站中可以找到
    title = title  # 改成你要的标题内容
    content = content  # 改成你要的正文内容
    url = 'http://www.pushplus.plus/send'
    data = {
        "token": token,
        "title": title,
        "content": content,
        "channel": "cp",
        "webhook": "100001"
    }
    body = json.dumps(data).encode(encoding='utf-8')
    headers = {'Content-Type': 'application/json'}
    requests.post(url, data=body, headers=headers)
    print("pushplus服务已启动，所有账号结果已推送✔")


@timeout(60)
def getID(address, key):
    global ID
    address = address[:-1]
    if address == "浦东新" or address == "双鸭" or address == "宝山":
        address = "上海"
    else:
        pass
    url = f'https://geoapi.qweather.com/v2/city/lookup?location={address}&key={key}'
    datas = requests.get(url).json()
    # print(data)
    # print(type(datas))
    for data in datas['location']:
        if data['name'] == address:
            ID = data['id']
    return ID


@timeout(60)
def getData(address, address1, address2, ID, key):
    url = f'https://devapi.qweather.com/v7/weather/now?location={ID}&key={key}'
    datas = requests.get(url).json()
    data_time = datas['now']['obsTime']  # 观测时间
    data_time = re.findall(r'\d+', str(data_time))
    time = re.findall(r'\d+', str(data_time))
    time = time[0] + time[1] + time[2]
    data_feelsLike = datas['now']['feelsLike']  # 体感温度
    data_text = datas['now']['text']  # 温度状态描述
    url_sun = f'https://devapi.qweather.com/v7/astronomy/sun?location={ID}&date={time}&key={key}'
    data_sun = requests.get(url_sun).json()
    data_sunrise = data_sun['sunrise']  # 日出
    data_sunrise = re.findall(r'\d+', str(data_sunrise))
    data_sunset = data_sun['sunset']  # 日落
    data_sunset = re.findall(r'\d+', str(data_sunset))
    data_sunrise[3] = list(data_sunrise[3])
    if data_sunrise[3][0] == "0":
        data_sunrise[3][0] = ""
    else:
        pass
    data_sunrise[3] = ''.join(data_sunrise[3])
    data_sunrise = data_sunrise[3] + '点' + data_sunrise[4] + '分'
    data_sunset = data_sunset[3] + '点' + data_sunset[4] + '分'
    data_time = data_time[1] + '月' + data_time[2] + '日' + data_time[3] + '点' + data_time[4] + '分'  # 观测时间
    url_daily = f'https://devapi.qweather.com/v7/air/now?location={ID}&key={key}'
    datas_daily = requests.get(url_daily).json()
    data_daily = datas_daily['now']['category']
    url_tip = f'https://devapi.qweather.com/v7/indices/1d?type=0&location={ID}&key={key}'
    datas_tip = requests.get(url_tip).json()
    data_tip = datas_tip['daily'][0]['text']
    # print(address + '  观测时间：' + data_time)
    if address1 == address2:
        a = '您当前处于：' + address2 + address
    else:
        a = '您当前处于：' + address1 + address2 + address
    # print('目前天气：' + data_text.replace('雪', '雪❄').replace('雷', '雷⚡').replace('沙尘', '沙尘🌪').replace('雾',
    # '雾🌫').replace(
    # '冰雹', '冰雹🌨').replace('多云', '多云☁').replace('小雨', '小雨🌧').replace('阴', '阴🌥').replace('晴', '晴🌤')
    # + '\n' + '体感温度：' + data_feelsLike + '℃' + " 🍀")
    b = ('目前天气：' + data_text.replace('雪', '雪❄').replace('雷', '雷⚡').replace('大雨', '大雨🌧').replace('沙尘',
                                                                                                            '沙尘🌪').replace(
        '雾',
        '雾🌫').replace(
        '冰雹', '冰雹🌨').replace('多云', '多云☁').replace('小雨', '小雨🌧').replace('中雨', '中雨🌧').replace('阴',
                                                                                                            '阴🌥').replace(
        '晴',
        '晴🌤')
         + '\n' + '体感温度：' + data_feelsLike + '℃' + " 🍀")
    # print('空气质量：' + data_daily)
    c = '空气质量：' + data_daily.replace('优', '优⭐').replace('良', '良▲')
    # print('日出：' + '凌晨' + data_sunrise + '☀' + '\n' + '日落：' + '傍晚' + data_sunset + '🌙')
    d = '日出：' + '凌晨' + data_sunrise + '☀' + '\n' + '日落：' + '傍晚' + data_sunset + '🌙'
    # print(data_tip)
    e = data_tip
    message = a + '\n' + b + '\n' + c + '\n' + d + '\n' + e
    return message


# 获取日期和倒计时
def get_time():
    a = datetime.datetime.now()  # 实施时间
    y = str(a.year)
    m = str(a.month)
    d = str(a.day)  # 转换为字符串，便于打印
    timenow = y + '年' + m + '月' + d + '日' + '\n'
    b = datetime.datetime(2022, 12, 25)  # 自己设置的研究生考试时间
    count_down = (b - a).days  # 考研倒计时
    return timenow, count_down


def get_file_content(file):
    with open(file, 'rb') as fp:
        return fp.read()


def img_to_str(image_path):
    image = get_file_content(image_path)
    result = client.basicGeneral(image)
    if 'words_result' in result:
        return '\n'.join([w['words'] for w in result['words_result']])


class qywx:
    corpid = 'wwa721a143a22ceed4'  # 步骤1-3中的企业id
    app_list = [
        (1000001, 'OZwYUc5FABoqJVonBioH3DekVeuvlf5pjkxLTdaHJus'),
        (1000002, 'OZwYUc5FABoqJVonBioH3DekVeuvlf5pjkxLTdaHJus')  # 此处将步骤1-2中的AgentId 和 Secret分别填入，多个应用逗号隔开
    ]

    def __init__(self, app_id):  # app_id 按app_list顺序编号
        self.agentid, self.corpsecret = qywx.app_list[app_id]

    # 上传临时文件素材接口，图片也可使用此接口，20M上限
    def post_file(self, filepath, filename):
        response = requests.get(
            "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}".format(
                corpid=qywx.corpid, corpsecret=self.corpsecret))
        data = json.loads(response.text)
        access_token = data['access_token']

        post_file_url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={access_token}&type=file".format(
            access_token=access_token)

        m = MultipartEncoder(
            fields={'file': (filename, open(filepath + filename, 'rb'), 'multipart/form-data')},
        )

        r = requests.post(url=post_file_url, data=m, headers={'Content-Type': m.content_type})
        js = json.loads(r.text)
        print("upload " + js['errmsg'])
        if js['errmsg'] != 'ok':
            return None
        return js['media_id']

    # 向应用发送图片接口，_message为上传临时素材后返回的media_id
    def send_img(self, _message, useridlist=['name1|name2']):
        useridstr = "|".join(useridlist)
        response = requests.get(
            "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}".format(
                corpid=qywx.corpid, corpsecret=self.corpsecret))
        data = json.loads(response.text)
        access_token = data['access_token']

        json_dict = {
            "touser": useridstr,
            "msgtype": "image",
            "agentid": self.agentid,
            "image": {
                "media_id": _message,
            },
            "safe": 0,
            "enable_id_trans": 1,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        json_str = json.dumps(json_dict)
        response_send = requests.post(
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}".format(
                access_token=access_token), data=json_str)
        print("send to " + useridstr + ' ' + json.loads(response_send.text)['errmsg'] + "\n")
        return json.loads(response_send.text)['errmsg'] == 'ok'

    # 向应用发送文字消息接口，_message为字符串
    def send_text(self, _message, useridlist=['name1|name2']):
        useridstr = "|".join(useridlist)  # userid 在企业微信-通讯录-成员-账号
        response = requests.get(
            "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}".format(
                corpid=qywx.corpid, corpsecret=self.corpsecret))
        data = json.loads(response.text)
        access_token = data['access_token']
        json_dict = {
            "touser": useridstr,
            "msgtype": "text",
            "agentid": self.agentid,
            "text": {
                "content": _message
            },
            "safe": 0,
            "enable_id_trans": 1,
            "enable_duplicate_check": 0,
            "duplicate_check_interval": 1800
        }
        json_str = json.dumps(json_dict)
        response_send = requests.post(
            "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}".format(
                access_token=access_token), data=json_str)
        print("send to " + useridstr + ' ' + json.loads(response_send.text)['errmsg'] + "\n")
        return json.loads(response_send.text)['errmsg'] == 'ok'


if __name__ == '__main__':
    print('''
    ------------------------------------------------------------------------------
     ____  _   _ _____ ____      ____ ____   ____   _____           _ 
    / ___|| | | | ____/ ___|    / ___|___ \ / ___| |_   _|__   ___ | |
    \___ \| | | |  _| \___ \    \___ \ __) | |       | |/ _ \ / _ \| |
     ___) | |_| | |___ ___) |    ___) / __/| |___    | | (_) | (_) | |
    |____/ \___/|_____|____/    |____/_____|\____|   |_|\___/ \___/|_|   V1.0

    SUES 体温填报工具 by FY 
    源码/Issue/贡献 https://github.com/666fy666/suestwtb 如果觉得好用别忘记Star哦！
    ------------------------------------------------------------------------------''')
    try:
        # 读取配置文件并检查
        # 设置以utf-8解码模式读取文件，encoding参数必须设置，否则默认以gbk模式读取文件，当文件中包含中文时，会报错
        f = open("config.json", encoding="utf-8")
        file = json.load(f)
        admin = file["admin"]
        adminemail = file["adminemail"]
        email = file["email"]
        not_show = file["not_show"]
        pushplus = file["pushplus"]
        weather = file["weather"]
        tips = file["tips"]
        config = []
        if email:
            config.append("●邮件推送:开启✔(账号和邮箱一对一推送)")
            if admin:
                config.append(
                    "●开发者模式:开启✔(所有邮件将会推送到开发者邮箱)" + "\n" + "●开发者邮箱：%s@qq.com" % adminemail)
            else:
                config.append("●开发者模式:关闭✖(所有邮件将会推送到开发者邮箱)")
            if weather:
                config.append("●查看天气(需先开启邮件推送):开启✔")
            else:
                config.append("●查看天气(需先开启邮件推送):关闭✖")
            if tips:
                config.append("●每日寄语(需先开启邮件推送):开启✔")
            else:
                config.append("●每日寄语(需先开启邮件推送):关闭✖")
        else:
            config.append("●邮件推送:关闭✖(账号和邮箱一对一推送)")
        if not_show:
            config.append("●隐藏网页:开启✔")
        else:
            config.append("●隐藏网页:关闭✖")
        if len(pushplus) > 5:
            config.append("●pushplus:开启✔(程序结束后将会收到所有账号填报结果)")
        else:
            config.append("●pushplus:关闭✖(程序结束后将会收到所有账号填报结果)")
        config = "\n".join(config)
        print("👇👇👇您の配置文件信息如下👇👇👇(请核对，如发现配置错误请停止运行本程序并修改配置文件):" + "\n" + config)
        print("=" * 80)
        time.sleep(3)
    except Exception as e:
        print("报错：%s" % e)
        print("请依照示例，检查并修正配置文件！！！本程序将在十秒后退出！！！")
        time.sleep(10)
        sys.exit()
    configocr = {
        'appId': '25963617',
        'apiKey': 'FkImi13Uj6Ry0irvgcAhoxq8',
        'secretKey': 'nrowIKYG7RgKHw2N0V06fURyFtFWNvXo'
    }
    client = AipOcr(**configocr)
    opt = Options()
    opt.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
    opt.add_argument('window-size=950x1035')  # 设置浏览器分辨率（宽，高）
    opt.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    opt.add_argument('user-agent=%s' % user_agent)
    if not_show:
        opt.add_argument('--headless')  # 浏览器不提供可视化界面。Linux下如果系统不支持可视化不加这条会启动失败
    userinfo()
    print("本次运行结束，本程序将在十秒后退出！！！")
    time.sleep(10)
