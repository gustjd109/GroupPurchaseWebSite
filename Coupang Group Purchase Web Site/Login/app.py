from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from pymongo import MongoClient
import jwt
import datetime
import hashlib

SECRET_KEY = 'JUNGLE'

app = Flask(__name__)

client = MongoClient('mongodb://hyunsung:hyunsung@43.201.61.139', 27017)
db = client.dbminiproject

# HTML을 주는 부분
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup')
def login():
    return render_template('signup.html')

@app.route('/main')
def signup():
    return render_template('main.html')

# 회원가입
@app.route('/api/signup', methods=['POST'])
def api_signup():
    ph_receive = request.form['ph_give']
    pw_receive = request.form['pw_give']
    nm_receive = request.form['nm_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # 이미 존재하는 아이디면 회원가입 실패
    result = db.user.find_one({'PHONENUMBER': ph_receive})
    if result is not None:
        return jsonify({'result': 'fail', 'msg': '이미 존재하는 ID입니다!'})
    else:
        db.user.insert_one({'PHONENUMBER': ph_receive, 'PASSWORD': pw_hash, 'NAME': nm_receive})
        return jsonify({'result': 'success'})

# 로그인
@app.route('/api/login', methods=['POST'])
def api_login():
    ph_receive = request.form['ph_give']
    pw_receive = request.form['pw_give']

    # 비밀번호 암호화
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # 전화번호와 암호화된 비밀번호를 소지한 유저 검색
    result = db.user.find_one({'PHONENUMBER': ph_receive, 'PASSWORD': pw_hash})

    # 전화번호와 암호화된 비밀번호를 소지한 유저 검색 성공 시, JWT 토큰 생성 및 발급
    if result is not None:
        # JWT 토큰 생성
        payload = {
            'PHONENUMBER': ph_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # 토큰 발급
        return jsonify({'result': 'success', 'token': token})
    # 유저 검색 실패 시,
    else:
        return jsonify({'result': 'fail', 'msg': '휴대폰 번호 또는 비밀번호가 일치하지 않습니다!'})

# 보안: 로그인한 사용자만 통과할 수 있는 API
@app.route('/api/isAuth', methods=['GET'])
def api_valid():
    token_receive = request.cookies.get('mytoken')
    try:
        # 시크릿키 토큰 디코딩
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # payload 안에 전화번호가 들어있으며, 해당 전화번호로 유저정보 검색
        userinfo = db.user.find_one({'PHONENUMBER': payload['PHONENUMBER']}, {'_PHONENUMBER': 0})
        return jsonify({'result': 'success', 'userph': userinfo['PHONENUMBER']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러 발생
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다!'})
    except jwt.exceptions.DecodeError:
        # 로그인 정보가 없으면 에러 발생
        return jsonify({'result': 'fail', 'msg': '로그인 정보가 존재하지 않습니다!'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)