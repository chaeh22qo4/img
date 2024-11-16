from flask import Flask, session, render_template, redirect, request, url_for
from flaskext.mysql import MySQL
import os
from werkzeug.utils import secure_filename

mysql =MySQL()
app=Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Rch22qo4@'
app.config['MYSQL_DATABASE_DB'] = 'board_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.secret_key = "ABCEDFG"
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

def get_categories():
    cursor.execute("SELECT * FROM categories")
    return cursor.fetchall()

@app.route('/', methods=['GET','POST'])
def main():
    error = None
    
    if request.method == 'POST':
        id=request.form['id']
        pw=request.form['pw']

        sql = "SELECT id FROM users WHERE id = %s AND pw = %s"
        value = (id, pw)
        cursor.execute("set names utf8")
        cursor.execute(sql, value)

        data=cursor.fetchall()

        for row in data:
            data = row[0]
        
        if data:
            session['login_user'] = id
            return redirect(url_for('home'))
        else:
            error = 'invalid input data detected !'
    return render_template('main.html', error = error)

@app.route('/register.html', methods=['GET', 'POST']) # 회원가입 화면
def register():
    error = None
 
    if request.method == 'POST': # POST 형식으로 요청할 것임
        # 페이지에서 입력한 값을 받아와 변수에 저장
        id = request.form['regi_id']
        pw = request.form['regi_pw']
 
        sql = "INSERT INTO users VALUES ('%s', '%s')" % (id, pw) # 실행할 SQL문
        cursor.execute(sql) # 메소드로 전달해 명령문을 실행
        data = cursor.fetchall() # 실행한 결과 데이터를 꺼냄
 
        if not data:
            conn.commit() # 변경사항 저장
            return redirect(url_for('main'))  # 로그인 화면으로 이동
 
        else:
            conn.rollback() # 데이터베이스에 대한 모든 변경사항을 되돌림
            return "Register Failed"
 
        cursor.close()
        conn.close()
 
    return render_template('register.html', error=error) # 용도 확인

@app.route('/home.html', methods=['GET']) # 로그인 된 후 홈 화면
def home():
    error = None
    categories = get_categories()  # 카테고리 목록 가져오기
    category_images = {}

    # 카테고리별로 이미지 조회
    for category in categories:
        category_id = category[0]
        cursor.execute("SELECT * FROM images WHERE category_id = %s",(category_id))
        category_images[category[1]] = cursor.fetchall()

    return render_template("home.html", categories=categories, category_images=category_images)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/write.html', methods=['GET','POST'])
def write():
    error = None
    categories = get_categories()  # 카테고리 목록 가져오기

    if request.method == "POST":
        # 제목, 파일, 카테고리 업로드 처리
        title = request.form['title']
        file = request.files['file']
        category_id = request.form['category']

        if file and allowed_file(file.filename) and category_id and title:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # 이미지 정보를 MySQL에 저장
            cursor.execute(
                "INSERT INTO images (filename, title, category_id) VALUES (%s, %s, %s)", (filename, title, category_id)
            )
            conn.commit()

            # 업로드 후 홈으로 리다이렉션
            return redirect(url_for('home'))

    return render_template("write.html", categories=categories)

if __name__ == '__main__':
    app.run()