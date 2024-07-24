from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

# 顯式等待
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import time
from time import sleep
from datetime import datetime

import pandas as pd
import numpy as np

import requests
import json
from pandas import DataFrame,json_normalize
from math import *

driver = webdriver.Chrome(executable_path="C://Program Files (x86)//Google//Chrome//Application//chromedriver.exe")
driver.maximize_window()
driver.implicitly_wait(10) #隱式等待，最長等待10秒

def find_viliage():
    global address_raw
    LoginUrl= ("https://addressrs.moi.gov.tw/address/index.cfm?city_id=68000")
    driver.get(LoginUrl)

    sleep(1)

    address = address_raw
    print(address)
    address_list = list(address)

    address = address[0:address_list.index("號")+1]

    if "區" not in address_list:
        address = "中壢區" + address

    if "市"    not in address_list:
        address = "桃園市" + address

    try:

        if "里" in address_list:
            print("地址有里")
            print(address[address_list.index("里")-2:address_list.index("里")+1])
            return address[address_list.index("里")-2:address_list.index("里")+1]
        
        print(address)

        driver.find_element_by_xpath('//*[@id="FreeText_ADDR"]').send_keys(address)
        driver.find_element_by_xpath('//*[@id="ext-gen51"]').click()

        sleep(2)

        viliage_address = driver.find_element_by_xpath('//*[@id="ext-gen92"]/div/table/tbody/tr/td[2]/div').text
        # print(viliage_address)
        print(viliage_address[3:6])
        print("------------------------")
    except:
        print("false")
        print("------------------------")

    viliage_df = pd.read_csv('viliage_UID.csv' , encoding = 'utf_8_sig')
    UID = ""

    for i in range(len(viliage_df)):
        if viliage_address[3:6] == viliage_df.at[i,'里']:
            UID = viliage_df.at[i,'UID']
    
    return UID

def find_land_no():
    global address_raw
    LoginUrl= ("https://easymap.land.moi.gov.tw/R02/Index#")
    driver.get(LoginUrl)

    sleep(1)

    address = address_raw
    print(address)
    address_list = list(address)

    del address_list[address_list.index("號")+1:]
    print(address_list)

    if "市" in address_list:
        del address_list[:3]

    # print(address_list)

    if "區" in address_list:
        del address_list[:3]

    # print(address_list)

    #------------------------------------

    i = 0
    road = ""
    while not(address_list[i].isdigit()):
        # print(address_list[i])
        i+=1

    road = "".join(address_list[:i])
    print(road)
    del address_list[:i]
    i = 0
    # print(address_list)

    #------------------------------------
    lane = ""
    if "巷" in address_list:
        i = 0
        while not("巷" == address_list[i]):
            # print(address_list[i])
            i+=1

        lane = "".join(address_list[:i])
        del address_list[:i+1]
        print("巷:",lane)
        i = 0
        # print(address_list)

    #------------------------------------

    alley = ""
    if "弄" in address_list:
        i = 0
        while not("弄" == address_list[i]):
            # print(address_list[i])
            i+=1

        alley = "".join(address_list[:i])
        del address_list[:i+1]
        print("弄:",alley)
        i = 0
        # print(address_list)
    num = ""
    num = "".join(address_list[:-1])
    print("號:",num)

    #------------------------------------

    
    driver.find_element_by_xpath('//*[@id="button_addr"]').click() #選門牌

    sleep(1)

    driver.find_element_by_name('plus_section10').click()

    # driver.find_element_by_id('select_city_id1').click()
    city = Select(driver.find_element_by_id('select_city_id1'))
    city.select_by_value('H') #選取 桃園市
    
    sleep(1)

    town = Select(driver.find_element_by_id('select_town_id1'))
    town.select_by_value('03') #選取 中壢區

    sleep(1)

    town = Select(driver.find_element_by_id('select_road_id'))
    town.select_by_value(road) #選取 路

    sleep(1)

    if len(lane) != 0: #巷
        driver.find_element_by_xpath('//*[@id="doorLaneId"]').send_keys(lane)
    if len(alley) != 0: #弄
        driver.find_element_by_xpath('//*[@id="doorAlleyId"]').send_keys(alley)
    if len(num) != 0: #號
        driver.find_element_by_xpath('//*[@id="doorNoId"]').send_keys(num)
    
    driver.find_element_by_xpath('//*[@id="door_botton"]').click() #查詢

    sleep(5)

    driver.find_element_by_xpath('//*[@id="doorListId"]/ul[1]/li/a').click() #選取第一個

    detail_df = pd.DataFrame()

    table_1_text = driver.find_element_by_id('one-column-emphasis').text
    table_1_list = list(table_1_text.split('\n'))
    detail_1_list = []
    land_mark = []
    for detail in table_1_list:
        if detail[0:2] == '地段':
            land_mark = detail.split(' ')[1:3]
        else:
            detail_1_list.append(detail.split(' ')[0:2])

    del detail_1_list[0:3]

    detail_df['地號'] = land_mark
    print(land_mark)

    land_no_text = driver.find_element_by_xpath('//*[@id="info_contentDiv"]').text
    land_no_list = list(land_no_text.split(')'))
    land_no = land_no_list[1][:-2]
    
    for detail in detail_1_list:
        detail_df[detail[0]] = detail[1]

    # detail_df = detail_df.T
    print("---獲取地號完成---")

    driver.find_element_by_xpath('//*[@id="button_cada"]').click() #選門牌

    city = Select(driver.find_element_by_id('select_city_id'))
    city.select_by_value('H') #選取 桃園市
    
    sleep(1)

    town = Select(driver.find_element_by_id('select_town_id'))
    town.select_by_value('03') #選取 中壢區

    sleep(1)

    driver.find_element_by_xpath('//*[@id="land_button"]').click() #查詢

    sleep(5)

    table_2_text = driver.find_element_by_id('one-column-emphasis').text
    table_2_list = list(table_2_text.split('\n'))
    detail_2_list = []
    del table_2_list[0:3]
    del table_2_list[-1]

    for detail in table_2_list:
        detail_2_list.append(detail.split(' ')[0:2])
    
    for detail in detail_2_list:
        detail_df[detail[0]] = detail[1]

    # print(detail_df)

    # detail_df = detail_df.T
    print("---獲取土地現值---")
    
    #-------------------------------------------------------------------------------

    LoginUrl= ("https://landuse.tycg.gov.tw/Sys/QueryLandUse/QueryLandUse.aspx")
    driver.get(LoginUrl)

    sleep(1)

    town = Select(driver.find_element_by_id('ddlTownQuick'))
    town.select_by_value('03') #選取 中壢區

    sleep(1)

    Land_mark = Select(driver.find_element_by_id('ddlSectionQuick'))
    if len(land_mark[1]) > 3:
        landmark = land_mark[1][0:3] + ' ' + land_mark[1][3:]
    else:
        landmark = land_mark[1]
    Land_mark.select_by_visible_text(landmark) #選取 段

    sleep(1)

    driver.find_element_by_xpath('//*[@id="txtLandNo"]').send_keys(land_no)

    driver.find_element_by_xpath('//*[@id="btnLocateQuick"]').click()

    sleep(5)

    land_type = driver.find_element_by_id('lbl_ZoneName').text
    print(land_type)

    detail_df['土地分區'] = land_type
    print(detail_df)
    detail_df.to_csv("detail.csv", index = False,encoding="utf_8_sig")
    print("---獲取土地類型---")

    return land_type

def find_lat_lng():
    global address_raw

    GOOGLE_PLACES_API_KEY = ""

    address = address_raw
    print(address)
    address_list = list(address)

    address = address[0:address_list.index("號")+1]

    if "區" not in address_list:
        address = "中壢區" + address

    if "市"    not in address_list:
        address = "桃園市" + address
    
    #地址查經緯度
    res = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?address=中壢區{address}&language=zh-TW&key={GOOGLE_PLACES_API_KEY}")
    # print (res.text)

    sesarch_results = json.loads(res.text)
    if len(sesarch_results["results"]) != 0:
        print(sesarch_results["results"][0]["geometry"]["location"])
        
        lat = float(sesarch_results["results"][0]["geometry"]["location"]["lat"])
        lng = float(sesarch_results["results"][0]["geometry"]["location"]["lng"])
    else:
        print('false')

    return lat,lng

def str_2_timestamp(year):
    trade_date_str = f"{year}_01_01 00:00:00"
    trade_date_datetime = datetime.strptime(trade_date_str,'%Y_%m_%d %H:%M:%S')
    print(trade_date_datetime)

    UTC_datetime = datetime.strptime('1970_01_01 00:00:00','%Y_%m_%d %H:%M:%S')
    mettime = trade_date_datetime - UTC_datetime

    timestamp = mettime.days*24*3600 + mettime.seconds
    return timestamp

def Distance1(Lat_A,Lng_A,Lat_B,Lng_B): #第一種計算方法
    ra=6378.140 #赤道半徑
    rb=6356.755 #極半徑 （km）
    flatten=(ra-rb)/ra  #地球偏率
    rad_lat_A=radians(Lat_A)
    rad_lng_A=radians(Lng_A)
    rad_lat_B=radians(Lat_B)
    rad_lng_B=radians(Lng_B)
    pA=atan(rb/ra*tan(rad_lat_A))
    pB=atan(rb/ra*tan(rad_lat_B))
    xx=acos(sin(pA)*sin(pB)+cos(pA)*cos(pB)*cos(rad_lng_A-rad_lng_B))
    c1=(sin(xx)-xx)*(sin(pA)+sin(pB))**2/cos(xx/2)**2
    c2=(sin(xx)+xx)*(sin(pA)-sin(pB))**2/sin(xx/2)**2
    dr=flatten/8*(c1-c2)
    distance=ra*(xx+dr)
    return distance
#-----------------------------------------------------------------

import joblib
model_pretrained = joblib.load('house_price_predict_2022_05_28.pkl') #載入模型

#----------------------------建網站開始----------------------------

from flask import Flask, request, render_template
app = Flask(__name__) #建網站模組 #本地伺服器

# 外部連結自動生成套件 #連接外部伺服器
from flask_ngrok import run_with_ngrok

df = pd.read_csv('chungli_ML.csv' , encoding = 'utf_8_sig')

@app.route("/")
def formPage():
    return render_template('form.html') #去templates(名稱不能動)資料夾找form.html

address_raw = ""
lat = ""
lng = ""

@app.route("/submit", methods=['POST'])
def submit():
    global df,address_raw,address_raw,UID,lat,lng
    if request.method == 'POST':
        form_data = request.form #網站傳回的封包
        print(form_data)
        print(len(form_data))
        #-------------------------------------------
        address_raw = form_data['address']

        # UID = find_viliage()
        # land_type = find_land_no() #要開著視窗
        # land_type = "商業區"
        lat,lng = find_lat_lng()
        # print(lat)
        # print(lng)

        #--------------------------------------------

        #land_type 土地類型
        land_type_0 = ''
        land_type_1 = ''
        land_type_2 = ''
        land_type_3 = ''
        land_type_4 = ''
        land_type_5 = ''
        land_type_6 = ''

        if int(form_data['land_type']) == 0:
            land_type_0 = 'selected'
        elif int(form_data['land_type']) == 1:
            land_type_1 = 'selected'
        elif int(form_data['land_type']) == 2:
            land_type_2 = 'selected'
        elif int(form_data['land_type']) == 3:
            land_type_3 = 'selected'
        elif int(form_data['land_type']) == 4:
            land_type_4 = 'selected'
        elif int(form_data['land_type']) == 5:
            land_type_5 = 'selected'
        else:
            building_type_6 = 'selected'
        
        print('land_type')

        #building_type 建物型態
        building_type_0 = ''
        building_type_1 = ''
        building_type_2 = ''
        building_type_3 = ''

        if int(form_data['building_type']) == 0:
            building_type_0 = 'selected'
        elif int(form_data['building_type']) == 1:
            building_type_1 = 'selected'
        elif int(form_data['building_type']) == 2:
            building_type_2 = 'selected'
        else:
            building_type_3 = 'selected'

        print('building_type')

        #use 主要用途
        use_0 = ''
        use_1 = ''
        use_2 = ''
        use_3 = ''
        use_4 = ''
        use_5 = ''

        if int(form_data['use']) == 0:
            use_0 = 'selected'
        elif int(form_data['use']) == 1:
            use_1 = 'selected'
        elif int(form_data['use']) == 2:
            use_2 = 'selected'
        elif int(form_data['use']) == 3:
            use_3 = 'selected'
        elif int(form_data['use']) == 4:
            use_4 = 'selected'
        else:
            use_5 = 'selected'

        print('use')

        #conpartments 隔間
        conpartments_Yes = ''
        conpartments_No = ''
        if int(form_data['conpartments'])== 1:
            conpartments_Yes = 'checked'
        else:
            conpartments_No = 'checked'
        
        print('conpartments')

        #managment 管理室
        managment_Yes = ''
        managment_No = ''
        if int(form_data['managment'])== 1:
            managment_Yes = 'checked'
        else:
            managment_No = 'checked'

        print('managment')

        #note 備註
        note_Yes = ''
        note_No = ''
        if int(form_data['note'])== 1:
            note_Yes = 'checked'
        else:
            note_No = 'checked'
        
        print('note')

        #balcony 陽台
        balcony_Yes = ''
        balcony_No = ''
        if int(form_data['balcony'])== 1:
            balcony_Yes = 'checked'
        else:
            balcony_No = 'checked'
        
        print('balcony')

        #elevator 電梯
        elevator_Yes = ''
        elevator_No = ''
        if int(form_data['elevator'])== 1:
            elevator_Yes = 'checked'
        else:
            elevator_No = 'checked'
        
        print('elevator')

        #後處理--------------------------------------------------------------

        # land_type
        # land_district_list =list(land_type)
        # land_district = ""

        # if '農' in land_district_list:
        #     land_district = 1

        # elif '商' in land_district_list:
        #     land_district = 5
        # elif '市' in land_district_list:
        #     land_district = 5

        # elif '工' in land_district_list:
        #     if '甲' in land_district_list:
        #         land_district = 4
        #     else:
        #         land_district = 3
        # elif '倉' in land_district_list:
        #     land_district = 3

        # elif '公' in land_district_list:
        #     land_district = 7
        # elif '綠' in land_district_list:
        #     land_district = 7

        # elif '學' in land_district_list:
        #     land_district = 10
        # elif '體' in land_district_list:
        #     land_district = 10
        
        # elif '停' in land_district_list:
        #     land_district = 8
        # elif '鐵' in land_district_list:
        #     land_district = 8
        
        # elif '行' in land_district_list:
        #     land_district = 9
        # elif '廣' in land_district_list:
        #     land_district = 9
        # elif '關' in land_district_list:
        #     land_district = 9
        # elif '社' in land_district_list:
        #     land_district = 9
        # else:
        #     land_district = 0

        # print('land_type',land_district)

        #complete_time
        complete_time = int(str_2_timestamp(2021-int(form_data['building_age'])))

        print('complete_time',complete_time)

        #nearest_avg_price

        dis_list = []
        for j in range(len(df)):
            # print(float(df.at[j,'Lat']),float(df.at[j,'Lng']))
            Lat_A = float(lat)
            Lng_A = float(lng)
            Lat_B = float(df.at[j,'Lat'])
            Lng_B = float(df.at[j,'Lng'])
            if abs(Lat_A - Lat_B) <= 0.000001 and abs(Lng_A - Lng_B) <= 0.000001 :
                dis_list.append(0)
            else:
                distance = Distance1(Lat_A,Lng_A,Lat_B,Lng_B)
                distance = round(distance, 3)
                # print(f'{distance} km')
                dis_list.append(distance)
        df['x'] = dis_list
        dis_list = []
        
        df_min = df[df['x'] == df['x'].min()]
        price_min = df_min['per_m^2_price'].mean()
        df.pop('x')

        print('nearest_avg_price',price_min)

        # 'total_land_transfer_area', 'land_type', 'land', 'building',
        # 'parking_num', 'transfer_highest_floor',
        # 'transfer_floor_num', 'total_floor_num', 'building_type', 'use',
        # 'complete_time', 'total_building_transfer_area', 'rooms',
        # 'living rooms', 'bathrooms', 'conpartments', 'managment', 'note',
        # 'balcony', 'elevator', 'Lat', 'Lng', 'UID', 'nearest_avg_price'

        # model_pretrained.predict([[0,1,1,0,3,1,2,np.log(150),np.log(5000)]])

        print(form_data)

        #資料型態與建模時相同 順序也是
        # result = model_pretrained.predict([[np.float64(form_data['total_land_transfer_area']),np.int64(land_district),np.int64(form_data['land']),np.int64(form_data['building']),np.int64(form_data['parking_num']),np.int64(form_data['transfer_highest_floor']),np.int64(form_data['transfer_floor_num']),np.int64(form_data['total_floor_num']),np.int64(form_data['building_type']),np.int64(form_data['use']),np.int64(complete_time),np.float64(form_data['total_building_transfer_area']),np.int64(form_data['rooms']),np.int64(form_data['livingrooms']),np.int64(form_data['bathrooms']),np.int64(form_data['conpartments']),np.int64(form_data['managment']),np.int64(form_data['note']),np.int64(form_data['balcony']),np.int64(form_data['elevator']),np.float64(lat),np.float64(lng),np.int64(UID),np.float64(price_min)]])
        result = model_pretrained.predict([[np.float64(form_data['total_land_transfer_area']),np.int64(form_data['land_type']),np.int64(form_data['land']),np.int64(form_data['building']),np.int64(form_data['parking_num']),np.int64(form_data['transfer_highest_floor']),np.int64(form_data['transfer_floor_num']),np.int64(form_data['total_floor_num']),np.int64(form_data['building_type']),np.int64(form_data['use']),np.int64(complete_time),np.float64(form_data['total_building_transfer_area']),np.int64(form_data['rooms']),np.int64(form_data['livingrooms']),np.int64(form_data['bathrooms']),np.int64(form_data['conpartments']),np.int64(form_data['managment']),np.int64(form_data['note']),np.int64(form_data['balcony']),np.int64(form_data['elevator']),np.float64(lat),np.float64(lng),np.int64(UID),np.float64(price_min)]])
        print(f'Result:{result}')

        prediction = f'預測每平方公尺價格：{result[0]:.6f}'
        print(prediction)

        detail_df = pd.read_csv('detail.csv' , encoding = 'utf_8_sig')

        
        return render_template('form.html', 
        address = form_data['address'],
        total_land_transfer_area = form_data['total_land_transfer_area'],
        total_building_transfer_area = form_data['total_building_transfer_area'],
        building_age = form_data['building_age'],

        land_type_0 =  land_type_0,
        land_type_1 =  land_type_1,
        land_type_2 =  land_type_2,
        land_type_3 =  land_type_3,
        land_type_4 =  land_type_4,
        land_type_5 =  land_type_5,
        land_type_6 =  land_type_6,

        building_type_0 = building_type_0,
        building_type_1 = building_type_1,
        building_type_2 = building_type_2,
        building_type_3 = building_type_3,

        use_0 = use_0,
        use_1 = use_1,
        use_2 = use_2,
        use_3 = use_3,
        use_4 = use_4,
        use_5 = use_5,

        total_floor_num = form_data['total_floor_num'],
        transfer_floor_num = form_data['transfer_floor_num'],
        transfer_highest_floor = form_data['transfer_highest_floor'],
        land = form_data['land'],

        parking_num = form_data['parking_num'],
        rooms = form_data['rooms'],
        livingrooms = form_data['livingrooms'],
        bathrooms = form_data['bathrooms'],

        conpartments_Yes = conpartments_Yes,conpartments_No = conpartments_No,
        managment_Yes = managment_Yes,managment_No = managment_No,
        note_Yes = note_Yes,note_No = note_No,
        balcony_Yes = balcony_Yes,balcony_No = balcony_No,
        elevator_Yes = elevator_Yes,elevator_No = elevator_No
        ,prediction = prediction)

@app.route("/map", methods=['POST'])
def map():
    return render_template('big_map_try.html')

if __name__ == "__main__":
    run_with_ngrok(app)
    app.run()