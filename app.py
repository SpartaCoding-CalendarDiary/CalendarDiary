from flask import Flask, render_template, request, jsonify
import json
from settings import DATABASES
app = Flask(__name__)

from pymongo import MongoClient #dumps는 pymongo에서 제공해주는 util
from bson import json_util

client = MongoClient(f'mongodb://{DATABASES.get("username")}:{DATABASES.get("password")}@{DATABASES.get("address")}', 27017)
db = client.dbcalendardiary

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('calendar.html')

@app.route('/write')
def write():
   return render_template('write.html')

@app.route('/read')
def read():
   return render_template('read.html')

#(테스트용 링크)
@app.route('/menubar')
def menubar():
   return render_template('menubar.html')

@app.route('/aboutus')
def aboutus():
   return render_template('aboutus.html')


## API역할을 하는 부분
#유저가 작성한 글을 저장한다(front->server)
@app.route('/diaries', methods=['POST'])  # 은찬
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
        return jsonify({'msg': '저장실패'})#프론트-글쓰기페이지에서 저장실패라고 alert 띄워야.


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
    print(request)
    print(request.args)
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
