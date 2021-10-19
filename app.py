from flask import Flask, render_template
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb://test:test@디비서버주소', 27017)#서버주소는 git repository에는 올리지 않기
db = client.dbcalendardiary

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('calendar.html')

## API역할을 하는 부분
#유저가 작성한 글을 저장한다(front->server)
# @app.route('/diaries', methods=['POST'])#은찬
# def write_diary():
#     글변수명 = request.form['글_give']
#     사진변수명 = request.form['사진_give']
#     날짜변수명 = request.form['날짜_give']
#
#     doc = {
#         '글변수명':글_receive,
#         '사진변수명':사진_receive,
#         '날짜변수명':날짜_receive
#     }
#
#     db.디비콜렉션명.insert_one(doc)
#
#     return jsonify({'msg': '저장 완료!'})
#
#해당 날짜(key)의 글을 불러온다(server->front)
#이 API는 글을 실제로 불러올 때 & 글을 저장하기 전 해당 날짜의 글 작성 여부를 확인할 때. 총 2번 쓰일 것 같음
# @app.route('/diaries', methods=['GET'])#은찬
# def show_diary():
#     변수명 = db.디비콜렉션명.find_one({'찾을key': 찾을value})
#     return jsonify({'변수명s': 변수명})
#
#해당 날짜의 사진을 불러온다(server->front)
# @app.route('/calendar', methods=['GET'])#유진
# def read_calendar():
#     all변수명 = list(db.디비콜렉션명.find({},{'_id':False}))
#     return jsonify({'all~~변수명s': all~~변수명})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)