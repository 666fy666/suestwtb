import os
import cv2
import time
import json
import random
import base64
import smtplib
import requests
import ddddocr as docr
from os.path import join
from email.header import Header
from email.mime.text import MIMEText
from selenium.webdriver import Chrome
from email.mime.image import MIMEImage
from selenium.webdriver.common.by import By
from email.mime.multipart import MIMEMultipart
from selenium.webdriver.common.action_chains import ActionChains

File_Path = 'D:/Auto_Temp'
acc_file = 'acc.txt'
pwd_file = 'pwd.txt'
Digit_Path = '/Digit_Temp'
Digit_Xpath = "//*[@id='fm1']/div[4]/img"
Digit_Filename = '/digit.png'

with open(join(File_Path, acc_file), 'r+', encoding='utf-8') as f_acc:
    acc_ar = f_acc.read().splitlines()

with open(join(File_Path, pwd_file), 'r+', encoding='utf-8') as f_pwd:
    pwd_ar = f_pwd.read().splitlines()

print("正在读取账号信息")
time.sleep(1)
c = str(len(acc_ar))
print("读取完毕，本次将进行%s个账号填报" % c)


def main(i):
    driver = Chrome()
    driver.get('https://web-vpn.sues.edu.cn')
    # driver.maximize_window()
    time.sleep(2)
    accounts = acc_ar[i]
    pwd = pwd_ar[i]
    print("正在执行当前进程，学号为：%s" % accounts)
    driver.find_element_by_xpath(
        "//*[@id='username']").send_keys(accounts)
    driver.find_element_by_xpath(
        "//*[@id='password']").send_keys(pwd)
    Digit_save_path = join(File_Path, File_Path)
    with open(join(Digit_save_path, Digit_Filename), 'wb+') as d:
        d.write(driver.find_element_by_xpath(Digit_Xpath).screenshot_as_png)
    ocr = docr.DdddOcr()
    with open(join(Digit_save_path, Digit_Filename), 'rb') as d:
        img_bytes = d.read()
    res = ocr.classification(img_bytes)
    driver.find_element_by_xpath("//*[@id='authcode']").send_keys(str(res))
    driver.find_element_by_xpath("//*[@id='passbutton']").click()
    os.remove(join(Digit_save_path, Digit_Filename))
    time.sleep(2)
    driver.find_element_by_xpath("//*[@id='group-4']/div[2]/div/div[2]/p[2]").click()
    time.sleep(3)
    handles = driver.window_handles
    driver.switch_to.window(handles[1])
    a = random.uniform(36, 37)
    temprature = round(a, 1)
    print("系统随机生成体温：%s" % temprature)
    driver.find_element_by_xpath("//*[@id='form']/div[18]/div[1]/div/div[2]/div/div/input").clear()
    driver.find_element_by_xpath("//*[@id='form']/div[18]/div[1]/div/div[2]/div/div/input").send_keys(str(temprature))
    driver.find_element_by_xpath('//*[@id="post"]').click()
    try:
        error = driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div[3]')
        error.click()
    except Exception as e:
        time.sleep(2)
        background = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[1]/img[1]').get_attribute('src')
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
        slide_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[2]/div[2]')
        act = ActionChains(driver).drag_and_drop_by_offset(slide_btn, xoffset=result[0] - 27, yoffset=0)
        act.perform()
        act.release()
        os.remove('img.png')
        os.remove('background.png')
    # 设置有30次的重试机会
    for u in range(1, 30):
        try:
            time.sleep(2)
            driver.save_screenshot('%s.png' % accounts)
            driver.find_element(By.XPATH, '/html/body/div[3]/div[3]/a').click()
            print("第%s次滑动时成功" % u)
            print("学号：%s" % accounts)
            print("当前体温：%s" % temprature)
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
                slide_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div/div[2]/div[2]/div[2]')
                act = ActionChains(driver).drag_and_drop_by_offset(slide_btn, xoffset=result[0] - 27, yoffset=0)
                act.perform()
                act.release()
                os.remove('img.png')
                os.remove('background.png')
    return {'code': 403, 'status': 'error'}


if __name__ == '__main__':
    for i in range(len(acc_ar)):
        main(i)
