import yagmail

def test():
   # yag = yagmail.SMTP(user="support@autotestplat.com",password="Test123456",host="smtp.autotestplat.com")
    yag = yagmail.SMTP(user="zouhui1003it@163.com", password="200210208zouhui", host="smtp.163.com")
    contents = ['this is the body,and here is just text http:','you cnat find ','picture']
    yag.send('7980068@qq.com','subject',contents)

if __name__ == "__main__":
    test()