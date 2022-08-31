import base64
import os
import re
import time

import cv2
import ddddocr as docr
from selenium.webdriver import ActionChains
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

with open("acc.txt", 'r+', encoding='utf-8') as f_acc:
    acc_ar = f_acc.read().splitlines()
print("正在读取账号信息")
d = str(len(acc_ar))
print("读取完毕，本次将进行%s个账号填报" % d)


def main(i):
    opt = Options()
    opt.add_argument('--no-sandbox')  # 解决DevToolsActivePort文件不存在的报错
    opt.add_argument('window-size=1000x1150')  # 设置浏览器分辨率
    opt.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'
    opt.add_argument('user-agent=%s' % user_agent)
    # opt.add_argument('--hide-scrollbars')  # 隐藏滚动条，应对一些特殊页面
    # opt.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片，提升运行速度
    opt.add_argument('--headless')  # 浏览器不提供可视化界面。Linux下如果系统不支持可视化不加这条会启动失败
    driver = Chrome(options=opt)  # 创建Chrome无界面对象
    num = i + 1
    print("正在执行第%s个进程" % num)
    total = acc_ar[i]
    allin = re.split(r'[:：]', total)
    accounts = re.search(r'\w+', allin[0])
    accounts = accounts.group()
    pwd = allin[1]
    print("账号：【{}】，密码：【{}】".format(accounts, pwd))
    driver.get('https://webvpn.sues.edu.cn')
    driver.find_element_by_xpath("//*[@id='username']").send_keys(accounts)
    driver.find_element_by_xpath("//*[@id='password']").send_keys(pwd)
    with open("digit.png", 'wb+') as d:
        d.write(driver.find_element_by_xpath("//*[@id='fm1']/div[4]/img").screenshot_as_png)
    ocr = docr.DdddOcr()
    with open("digit.png", 'rb') as d:
        img_bytes = d.read()
    res = ocr.classification(img_bytes)
    os.remove("digit.png")
    driver.find_element_by_xpath("//*[@id='authcode']").send_keys(str(res))
    driver.find_element_by_xpath("//*[@id='passbutton']").click()
    try:
        time.sleep(3)
        driver.find_element_by_xpath(
            "//*[@id='__layout']/div/div/div[3]/div/div[2]/div/div[1]/div/div[1]/div/div[1]/a/div[2]/h2").click()
    except:
        time.sleep(3)
        driver.find_element_by_xpath("//*[@id='group-4']/div[2]/div/div[2]").click()
    time.sleep(2)
    print("登陆成功")
    handles = driver.window_handles
    driver.switch_to.window(handles[1])
    time.sleep(2)
    name = driver.find_element_by_xpath("//*[@id='form']/div[6]/div[1]/div/div[2]/div/div/span")
    who = str(name.text)
    driver.find_element_by_xpath('//*[@id="form"]/div[10]/div/div/div[2]/div/div/label[2]/div/ins').click()
    driver.find_element_by_xpath('//*[@id="form"]/div[18]/div/div/div[2]/div/div/label[1]/div/ins').click()
    driver.find_element_by_xpath('//*[@id="form"]/div[19]/div/div/div[2]/div/div/label[1]/div/ins').click()
    print("姓名：【{}】".format(who))
    driver.find_element_by_xpath('//*[@id="post"]').click()
    try:
        error = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div[3]')
        error.click()
    except Exception as e:
        time.sleep(2)
        background = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[1]/img[1]').get_attribute(
            'src')
        img1 = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[1]/img[2]').get_attribute('src')
        img1 = img1.split(',')
        background = background.split(',')
        i = base64.b64decode(img1[1])
        b = base64.b64decode(background[1])
        with open('img.png', 'wb+') as d:  # 保存验证码图片
            d.write(i)
        with open('background.png', 'wb+') as d:  # 保存验证码图片
            d.write(b)
        bg_img = cv2.imread('background.png')  # 背景图片
        tp_img = cv2.imread('img.png')  # 缺口图片
        bg_edge = cv2.Canny(bg_img, 100, 200)
        tp_edge = cv2.Canny(tp_img, 100, 200)
        bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
        tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
        res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        th, tw = tp_pic.shape[:2]
        tl = max_loc
        result = (tl[0] + tw / 2, tl[1] + th / 2)
        os.remove('img.png')
        os.remove('background.png')
        slide_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[2]/div[2]')
        act = ActionChains(driver).drag_and_drop_by_offset(slide_btn, xoffset=result[0] - 27, yoffset=0)
        act.perform()
        act.release()
    for u in range(1, 99):  # 设置有30次的重试机会
        try:
            driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
            time.sleep(2)
            driver.save_screenshot('log/%s.png' % accounts)
            driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/a').click()
            time.sleep(2)
            driver.quit()
            print("第%s次滑动时成功" % u)
            print("账号：%s,填报成功" % accounts)
            print("="*60)
            return {'code': 200, 'status': 'success'}
        except Exception as e:
            print("第%s次滑动失败，正在重试" % u)
            try:
                error = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div[3]')
                error.click()
            except Exception as e:
                time.sleep(2)
                background = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[1]/img[1]').get_attribute(
                    'src')
                img1 = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[1]/img[2]').get_attribute('src')
                img1 = img1.split(',')
                background = background.split(',')
                i = base64.b64decode(img1[1])
                b = base64.b64decode(background[1])
                with open('img.png', 'wb+') as d:  # 保存验证码图片
                    d.write(i)
                with open('background.png', 'wb+') as d:  # 保存验证码图片
                    d.write(b)
                bg_img = cv2.imread('background.png')  # 背景图片
                tp_img = cv2.imread('img.png')  # 缺口图片
                bg_edge = cv2.Canny(bg_img, 100, 200)
                tp_edge = cv2.Canny(tp_img, 100, 200)
                bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
                tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)
                res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                th, tw = tp_pic.shape[:2]
                tl = max_loc
                result = (tl[0] + tw / 2, tl[1] + th / 2)
                os.remove('img.png')
                os.remove('background.png')
                slide_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[2]/div[2]')
                act = ActionChains(driver).drag_and_drop_by_offset(slide_btn, xoffset=result[0] - 27, yoffset=0)
                act.perform()
                act.release()


if __name__ == '__main__':
    start = time.perf_counter()
    for i in range(len(acc_ar)):
        for c in range(1, 30):  # 设置有30次的重试机会
            try:
                main(i)
                break
            except Exception as e:
                print("该账号本次填报失败，进程即将重新挂起！")
                print("报错原因:%s" % e)
    end = time.perf_counter()
    alltime = round(end - start)
    print("本次运行时间为", round(alltime / 60, 2), '分钟')
    print("已经完成%s个账号填报，本进程将在5秒后退出！" % d)
    time.sleep(5)
