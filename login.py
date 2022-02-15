import random
import time
import cv2
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import base64
import ddddocr as docr
import os
from os.path import join

bro = Chrome()

File_Path = ''
Digit_Path = '/Digit_Temp'
Digit_Xpath = "//*[@id='fm1']/div[4]/img"
Digit_Filename = '/digit.png'


# bro.maximize_window()


def start_slide():
    try:
        error = bro.find_element_by_xpath('/html/body/div[4]/div/div/div/div[2]/div[3]')
        error.click()
    except Exception as e:
        time.sleep(2)
        background = bro.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[1]/img[1]').get_attribute('src')
        img1 = bro.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[1]/img[2]').get_attribute('src')
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
        slide_btn = bro.find_element(By.XPATH, '/html/body/div[4]/div/div/div/div[2]/div[2]/div[2]')
        act = ActionChains(bro).drag_and_drop_by_offset(slide_btn, xoffset=result[0] - 27, yoffset=0)
        act.perform()
        act.release()
        os.remove('img.png')
        os.remove('background.png')


def main():
    bro.get('https://web-vpn.sues.edu.cn/')
    bro.implicitly_wait(2)
    username = bro.find_element(By.XPATH, '//*[@id="username"]')
    password = bro.find_element(By.XPATH, '//*[@id="password"]')
    username.send_keys('')  # 输入用户名
    password.send_keys('')  # 输入密码
    Digit_save_path = join(File_Path, Digit_Path)
    try:
        with open(join(Digit_save_path, Digit_Filename), 'wb+') as d:
            d.write(bro.find_element_by_xpath(Digit_Xpath).screenshot_as_png)
        ocr = docr.DdddOcr()
        with open(join(Digit_save_path, Digit_Filename), 'rb') as d:
            img_bytes = d.read()
        res = ocr.classification(img_bytes)
        bro.find_element_by_xpath("//*[@id='authcode']").send_keys(str(res))
        bro.find_element(By.XPATH, '//*[@id="passbutton"]').click()
    except Exception as e:
        pass
    # 在输入用户名和密码之后,点击登陆按钮
    time.sleep(2)
    os.remove(join(Digit_save_path, Digit_Filename))
    WebDriverWait(bro, 5, 0.5).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[4]/div[2]/div/div[2]/p[1]')))
    bro.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[2]/div[4]/div[2]/div/div[2]/p[1]').click()
    bro.switch_to.window(bro.window_handles[-1])
    # randomly choose a temperature
    a = random.uniform(36, 37)
    temprature = round(a, 1)
    print(temprature)
    time.sleep(1)
    bro.find_element_by_xpath("//*[@id='form']/div[18]/div[1]/div/div[2]/div/div/input").clear()
    bro.find_element_by_xpath("//*[@id='form']/div[18]/div[1]/div/div[2]/div/div/input").send_keys(str(temprature))
    WebDriverWait(bro, 5, 0.5).until(EC.presence_of_element_located((By.XPATH, '//button[@id="post"]')))
    submit = bro.find_element(By.XPATH, '//button[@id="post"]')
    submit.click()
    start_slide()
    time.sleep(1)
    # 设置有30次的重试机会
    for i in range(1, 30):
        try:
            time.sleep(2)
            bro.save_screenshot('1.png')
            bro.find_element(By.XPATH, '/html/body/div[4]/div[3]/a').click()
            print("第%s次滑动时成功" % i)
            return {'code': 200, 'status': 'success'}
        except Exception as e:
            # print(e)
            print("第%s次滑动失败，正在重试" % i)
            start_slide()
    return {'code': 403, 'status': 'error'}


if __name__ == '__main__':
    ret = main()
bro.quit()

