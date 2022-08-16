import os
import smtplib
import time
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
from pandas import ExcelWriter


class email:
    def __init__(self, account, passward):
        self.account = account
        self.passward = passward
        self.content = ''
        self.login()
    
    def login(self):
        self.smtp = smtplib.SMTP(host="smtp.gmail.com", port="587")  # 設定SMTP伺服器
        try:
            self.smtp.ehlo()  # 驗證SMTP伺服器
            self.smtp.starttls()  # 建立加密傳輸
            self.smtp.login(self.account, self.passward)  # 登入寄件者gmail
            # smtp.send_message(content)  # 寄送郵件
            print("\nEmail Login Complete!\n")
        except Exception as e:
            print("\nError message: \n", e)
            print('process exit')
            exit()

    def clean(self):
        self.content = '' 
        self.smtp = ''

    def edit_content(self, to, subject, text):
        self.content = MIMEMultipart()  # 建立MIMEMultipart物件
        self.content["from"] = self.account
        self.content["subject"] = subject
        self.content["to"] = to 
        self.content.attach(MIMEText(text))  # 郵件純文字內容
    
    def sent(self):
        self.login()
        self.smtp.send_message(self.content)
        print('Email Sent Complete!')


class rateHDDTable:
    def __init__(self):
        print('init rate HDD table')

    def readTable(self, path):
        self.taskTable = pd.read_excel(path)
        self.path = path
    
    def updataTable(self, index, item, value):
        self.taskTable.loc[index,item] = value
        # print(self.taskTable)
        self.taskTable.to_excel(self.path, index=False)

    def getIndex(self):
        return self.taskTable.index

    def showTable(self):
        print('\n'*2)
        print(self.taskTable)
        print('\n'*2)


# https://www.geeksforgeeks.org/python-monitor-hard-disk-health-using-smartmontools/
class Device():
    def __init__(self):
        self.device_name = None
        self.title = ''
        self.value = ''

   # get the device info (sda or sdb)
    def get_device_info(self):
        cmd = 'df -h ' + self.device_name
        data = os.popen(cmd)
        res = data.read().splitlines()
        title = res[0]
        value = res[1]

        self.title = title
        self.value = value
  
def getTime():
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區
    fullTime = dt2.strftime("%Y-%m-%d %H:%M:%S")
    Y = dt2.strftime("%Y")
    M = dt2.strftime("%m")
    D = dt2.strftime("%d")
    H = dt2.strftime("%H")
    M = dt2.strftime("%M")
    S = dt2.strftime("%S")
    return Y, M, D, H, M, S, fullTime


# driver function
if __name__ == '__main__':
    # login 
    email_count = 1
    myEmail = email('samhuang8401@gmail.com', 'swxawilwdytlenoo')
    # myEmail.edit_content('samhuang@via.com.tw', '123444', 'test')
    # myEmail.sent()
    # exit()

    # HDD table
    HDDable = rateHDDTable()
    HDDable.readTable('./usagehdd.xlsx')
    HDDable.showTable()
    index = HDDable.getIndex()
    # detect table index
    try:
        indexNow = index.to_numpy()[-1]
        print('found index: ', indexNow)
    except:
        indexNow = 0
    # setting detect time
    routineH = ['00','01','02','03','04','05','06','07',
                '08','09','10','11','12','13','14','15'
                '16','17','18','19','20','21','22','23']


    device = Device()
    device.device_name = '/home/zimdytsai'

    while(True):
        Y, M, D, H, M, S, fullTime = getTime()
        print(fullTime)

        if str(H) in routineH and str(M) == '00' and str(S) == '00':
            indexNow = indexNow + 1
            device.get_device_info()
            title = device.title.split()
            value = device.value.split()

            for i in zip(title, value):
                HDDable.updataTable(indexNow,'time',  str(H))
                HDDable.updataTable(indexNow,'date',  str(fullTime))
                HDDable.updataTable(indexNow, str(i[0]), str(i[1]))

            use_index = title.index('Use%')
            usage = int(value[use_index][:-1])
            if usage >= 72:
                myEmail.edit_content('samhuang@via.com.tw', 'machine HDD warning!', 'HDD usage achieve: ' + str(usage) + '  (max:100)')
                myEmail.sent()
                myEmail.clean()
                email_count = email_count + 1
                if email_count > 1000:
                    print('email over')
                    exit()

            HDDable.showTable()
        time.sleep(1)

