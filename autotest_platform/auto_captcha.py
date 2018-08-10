# coding:utf-8
from PIL import Image
import os

def get_captcha(driver,captcha_id='kaptchaImage',full_screen_img_path='c:/web.png',
                  captcha_img_path='c:/captcha.png',captcha_final_path='c:/captcha_final.png',
                  txt_path='c:/captcha.txt'):
    #浏览器界面截图
    driver.save_screenshot(full_screen_img_path)
    #找到验证码图片，得到它的坐标
    element=driver.find_element_by_id(captcha_id)
    left = element.location['x']
    top = element.location['y']
    right = element.location['x'] + element.size['width']
    bottom = element.location['y'] + element.size['height']
    left,top,right,bottom = int(left),int(top),int(right),int(bottom)
    img = Image.open(full_screen_img_path)
    img = img.crop((left, top, right, bottom))
    #得到验证码图片
    img.save(captcha_img_path)
    #打开验证码图片
    img=Image.open(captcha_img_path)
    #颜色直方图，255种颜色，255为白色
    his=img.histogram()
    # values={}
    # for i in range(256):
    #     values[i]=his[i]
    # for j,k in sorted(values.items(),key=lambda x:x[1],reverse = True)[:20]:
    #     print('颜色：'+str(j),'数量：'+str(k))
    #新建一张图片(大小和原图大小相同，背景颜色为255白色)
    img_new=Image.new('P',img.size,255)
    for x in range(img.size[1]):
        for y in range(img.size[0]):
            #遍历图片的xy坐标像素点颜色
            pix=img.getpixel((y,x))
            # print(pix)
            #自己调色，r=0，g=0，b>0为蓝色
            if pix[0]<20 and pix[1]<20 and pix[2]>50:
                #把遍历的结果放到新图片上，0为透明度，不透明
                img_new.putpixel((y,x),0)
    img_new.save(captcha_final_path,format='png')

    #通过tesseract工具解析验证码图片，生成文本
    cmd='tesseract '+captcha_final_path+' '+txt_path[0:-4]
    os.system(cmd)

    #读取txt文件里面的验证码
    with open(txt_path,'r') as f:
        #去掉左右空格
        t=f.read().strip()
        #去掉中间空格
        if ' ' in t:
            t=t.replace(' ','')
        #如果是数字且长度为4，就返回数字，如果不是就返回 fail
        if t.isdigit() and len(t)==4:
            return t
        else:
            return 'fail'