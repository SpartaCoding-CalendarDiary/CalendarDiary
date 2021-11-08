from flask import Flask, render_template, request, jsonify, redirect, url_for
import jwt
import datetime
import hashlib
import json
from settings import DATABASES
from datetime import datetime, timedelta

app = Flask(__name__)

from pymongo import MongoClient #dumps는 pymongo에서 제공해주는 util
from bson import json_util

SECRET_KEY = 'SPARTA'
client = MongoClient(f'mongodb://{DATABASES.get("username")}:{DATABASES.get("password")}@{DATABASES.get("address")}', 27017)
db = client.dbcalendardiary

## HTML을 주는 부분
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/write')
def write():
   return render_template('write.html')

@app.route('/read')
def read():
   return render_template('read.html')

@app.route('/menubar')
def menubar():
   return render_template('menubar.html')

@app.route('/aboutus')
def aboutus():
   return render_template('aboutus.html')

@app.route('/calendar')
def calendar():
   return render_template('calendar.html')

@app.route('/login')
def login():
    msg = request.args.get('msg')
    return render_template('login.html', msg=msg)

@app.route('/register')
def register():
   return render_template('register.html')

## API역할을 하는 부분

# Login Sever
@app.route('/login', methods=['POST'])
def sign_in():
    # 로그인
    name_receive = request.form['name_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'name': name_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'name': name_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

# 회원가입 Server
@app.route('/register/save', methods=['POST'])
def sign_out():
    username_receive = request.form['name']
    password_receive = request.form['password']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    doc = {
        "name": username_receive,
        "password": password_hash
    }

    db.users.insert_one(doc)

    return jsonify({'result': 'success'})

# id 중복확인 Server
@app.route('/register/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

#좋아요
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        # Like Update API
        user_info = db.users.find_one({"name": payload["name"]})
        date_receive = request.form["date_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "date": date_receive,
            "name": user_info["name"],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"date": date_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})

        return jsonify({"result": "success", 'msg': 'updated'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


#유저가 작성한 글을 저장한다(front->server)
@app.route('/diaries', methods=['POST'])
def write_diary():
    text_receive = request.form['text_give']
    img_receive = request.form['img_give'] # img path
    date_receive = request.form['date_give']
    name_receive = request.form['name_give']
    doc = {
        'text': text_receive,
        'img': img_receive,
        'date': date_receive,
        'name': name_receive
    }
    #print(doc)
    # DB에 해당 날짜에 저장된 사진 있나 확인하기 위해 DB에서 date를 조건으로 돌아오는 객체가 있나 확인.
    result = db.diaries.find_one({'date': date_receive}, {'_id': False})

    # DB에서 가져온 값이 null이면(해당 날짜로 저장된 다이어리가 없으면) DB에 저장하기
    if not result:
        db.diaries.insert_one(doc)
        return jsonify({'msg': '저장성공'})  #프론트-글저장성공alert->calendar페이지로 이동해야함
    # 가져온 값이 null이 아니면(해당 날짜로 저장된 다이어리가 있으면) DB에 저장하지 않기.
    else:
        return jsonify({'msg': '일기는 하루에 한번만 쓸 수 있어요!'})#프론트-글쓰기페이지에서 저장실패라고 alert 띄워야.


#해당 날짜(key)의 글을 불러온다(server->front)
#이 API는 글을 실제로 불러올 때
#test - http://localhost:5000/diaries?date_give=2021-10-01
@app.route('/diaries', methods=['GET'])
def show_diary():
    date_receive = request.args.get('date_give')
    diary = db.diaries.find_one({'date':date_receive},{'_id':False})
    diary = json.loads(json_util.dumps(diary))
    return ({'diary': diary})


#해당 날짜의 사진을 불러온다(server->front)
@app.route('/calendar', methods=['GET'])
def read_calendar():
    allPic = list(db.diaries.find({},{'_id':False}))
    #print(allPic)
    return jsonify({'allPics': allPic})


#다이어리 삭제
@app.route('/delete', methods=['GET'])
def delete_diary():
    date_receive = request.args.get('date_give')
    #print(date_receive)
    result = db.diaries.delete_one({'date': date_receive})
    print(result)
    if result is not None:
        msg = "삭제완료"
    else:
        msg = "삭제실패"
    return jsonify({'msg': msg})


#다이어리 수정
@app.route('/update', methods=['GET'])
def update_diary():
    #print(request)
    #print(request.args)
    date_receive = request.args.get('date_give')
    text_receive = request.args.get('text_give')
    result = db.diaries.update_one({'date':date_receive},{'$set':{'text':text_receive}})
    if result is not None:
        msg = "수정완료"
    else:
        msg = "수정실패"
    return jsonify({'msg': msg})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)
