from selenium import webdriver
import time
from flask import Flask, render_template, jsonify, request
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.dbjungle

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/memo', methods=['POST'])
def saving():
    # url
    url_receive=request.form['url_give']
    # 등록자 이름
    # name_receive=request.form['name_give']
    # 등록자 핸드폰 번호
    phone_receive=request.form['phone_give']
    # 카톡 넘겨주기
    kakao_receive=request.form["kakao_give"]

    # url 변수에 저장
    url = url_receive

    interval = 2 

    # 데이터를 담을 리스트
    data_list = []


    # 크롬 웹드라이버
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # options.add_experimental_option("headless", True)
    driver = webdriver.Chrome("./chromedriver",options=options)  
    driver.get(url)   
    time.sleep(interval)

    # 크롤링
    myimg = driver.find_element_by_class_name('prod-image__detail').get_attribute("src")
    mytitle = driver.find_element_by_class_name('prod-buy-header__title').text
    myprice = driver.find_element_by_class_name('total-price').text


    result = {'myimg':myimg, 'mytitle' : mytitle, 'myprice' : myprice, 'myphone' : phone_receive, 'mykakao' : kakao_receive, 'myurl' : url_receive}

    # db 저장해야 함

    db.coupang.insert_one(result)
    
    return jsonify({'result': 'success'})

@app.route('/memo', methods=['GET'])
def listing():
    print('여까진 오니')
    result=list(db.coupang.find({},{'_id':0}))
    # result=list(db.memos.find().sort('like', -1))
    print('여까진 오니 시즌2')

    return jsonify({'result':'success', 'coupang':result })

@app.route('/delete', methods=['POST'])
def delete_star():
    phone_receive = request.form['phone_give']
    db.coupang.delete_one({'myphone': phone_receive})
    return jsonify({'result': 'success'})