from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb://test:test@비밀', 27017)

db = client.dbcalendardiary

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('calendar.html')

@app.route('/write')
def write():
   return render_template('write.html')

#(테스트용 링크)
@app.route('/menubar')
def menubar():
   return render_template('menubar.html')

@app.route('/aboutus')
def menubar():
   return render_template('aboutus.html')

## API역할을 하는 부분
#유저가 작성한 글을 저장한다(front->server)
@app.route('/diaries', methods=['POST'])  # 은찬
def write_diary():
    text_receive = request.form['text_give']
    img_receive = request.form['img_give']
    date_receive = request.form['date_give']
    name_receive = request.form['name_give']

    doc = {
        'text': text_receive,
        'img': img_receive,
        'date': date_receive,
        'name': name_receive
    }

    db.diaries.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})

#
#해당 날짜(key)의 글을 불러온다(server->front)
#이 API는 글을 실제로 불러올 때
# @app.route('/diaries', methods=['GET']) #은찬
# def show_diary():
#     변수명 = db.diaries.find_one({'찾을key': 찾을value})
#     return jsonify({'변수명s': 변수명})
#
#해당 날짜의 사진을 불러온다(server->front)
# @app.route('/calendar', methods=['GET'])#유진
# def read_calendar():
#     all변수명 = list(db.diaries.find({},{'_id':False}))
#     return jsonify({'all~~변수명s': all~~변수명})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)