from flask import Flask, render_template, request, jsonify, redirect
from pymongo import MongoClient
app = Flask(__name__)

client = MongoClient('mongodb://test:test@13.125.65.246', 27017)#서버주소는 git repository에는 올리지 않기

db = client.dbcalendardiary

## HTML을 주는 부분
@app.route('/')
def home():
   return render_template('calendar.html')

@app.route('/write')
def write():
   return render_template('write.html')

## API역할을 하는 부분
#유저가 작성한 글을 저장한다(front->server)
@app.route('/diaries', methods=['POST'])
def write_diary():
    text_receive = request.form['text_give']
    img_receive = request.form['img_give']
    date_receive = request.form['date_give']
    name_receive = request.form['name_give']

    #DB에 해당 날짜에 저장된 사진 있나 확인하기 위해 DB에서 date를 조건으로 돌아오는 객체가 있나 확인.
    result = db.diaries.find_one({'date': date_receive}, {'_id':False})

    #DB에서 가져온 값이 null이면(해당 날짜로 저장된 다이어리가 없으면) DB에 저장하기
    if not result:
        doc = {
            'text': text_receive,
            'img': img_receive,
            'date': date_receive,
            'name': name_receive
        }
        db.diaries.insert_one(doc)
        return redirect('/')#글 작성 완료 후 calendar페이지로 이동한다
    #가져온 값이 null이 아니면(해당 날짜로 저장된 다이어리가 있으면) DB에 저장하지 않기.
    else:
        return redirect('/write')#글 작성 실패 후 다시 글쓰기 페이지 redirect
        #질문. redirect때 /write페이지로 옮기고 + 실패 alert 띄우기 위한 msg같이 담으려면?
        #return jsonify({'msg': '중복!'})


#해당 날짜(key)의 글을 불러온다(server->front)
#이 API는 글을 실제로 불러올 때
# @app.route('/diaries', methods=['GET']) #은찬
# def show_diary():
#     변수명 = db.디비콜렉션명.find_one({'찾을key': 찾을value})
#     return jsonify({'변수명s': 변수명})



#해당 날짜의 사진을 불러온다(server->front)
@app.route('/calendar', methods=['GET'])
def read_calendar():
     allPic = list(db.diaries.find({},{'_id':False}))
     print(allPic)
     return jsonify({'allPics': allPic})
#선진님 front페이지에서 GET해올때 쓸 변수명은 allPics. allPics리스트 안에 사진과 날짜가 여러개 들어있다.

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)