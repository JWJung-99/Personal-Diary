from flask import Flask, render_template, session, url_for, request, redirect
from werkzeug.utils import secure_filename
import pymysql
import os


app = Flask(__name__)
app.secret_key = 'software engineering'

def connectsql():
    conn = pymysql.connect(host='localhost', user='root', passwd='0000', db='users', charset='utf8')
    return conn

@app.route('/')
def index():
    if 'username' in session:
        username = session['username']
        return render_template('index.html', logininfo = username)
    else:
        username = None
        return render_template('index.html', logininfo = username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userID = request.form['ID']
        userPW = request.form['PW']

        logininfo = request.form['ID']

        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT * FROM user_info WHERE user_ID = %s AND user_PW = %s"
        value = (userID, userPW)
        cursor.execute(query, value)
        data = cursor.fetchall()
        cursor.close()
        conn.close()

        for row in data:
            data = row[0]
        if data:
            session['username'] = request.form['ID']
            session['password'] = request.form['PW']
            return render_template('index.html', logininfo = logininfo)
        else:
            return render_template('loginErr.html')
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        userID = request.form['ID']
        userPW = request.form['PW']

        conn = connectsql()
        cursor = conn.cursor()
        query = "SELECT * FROM user_info WHERE user_ID = %s"
        value = userID
        cursor.execute(query, value)
        data = cursor.fetchall()

        if data:
            return render_template('signupErr.html')

        else:
            query = "INSERT INTO user_info (user_ID, user_PW) values (%s, %s)"
            value = (userID, userPW)
            cursor.execute(query, value)
            data = cursor.fetchall()
            conn.commit()
            return render_template('signupSuc.html')
            
        cursor.close()
        conn.close()

    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/timeline')
def timeline():
    if 'username' in session:
        username = session['username']
    else:
        username = None
    
    conn = connectsql()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    query = "SELECT Num, Title, WDate FROM diary ORDER BY Num DESC"
    cursor.execute(query)
    diarylist = cursor.fetchall()
    
    cursor.close()
    conn.close()

    return render_template('timeline.html', diarylist = diarylist, logininfo = username)

@app.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
            
            userTitle = request.form['title']
            userContent = request.form['content']

            conn = connectsql()
            cursor = conn.cursor() 
            query = "INSERT INTO diary (Title, Content) values (%s, %s)"
            value = (userTitle, userContent)
            cursor.execute(query, value)
            conn.commit()

            f = request.files['file']
            if not os.path.exists('./uploads/'):
                os.makedirs('./uploads')
            f.save('./uploads' + secure_filename(f.filename))

            return redirect(url_for('timeline'))

            cursor.close()
            conn.close()
    
    else:
        if 'username' in session:
            username = session['username']
            return render_template ('create.html', logininfo = username)


@app.route('/timeline/view/<Num>')
def view(Num):
    if 'username' in session:
        username = session['username']

        conn = connectsql()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        query = "SELECT Title, Content, Num From diary WHERE Num = %s"
        value = Num
        cursor.execute(query, value)
        diarycontent = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('view.html', data = diarycontent, logininfo = username)

@app.route('/timeline/edit/<Num>', methods=['GET', 'POST'])
def edit(Num):
    if request.method == 'POST':
        if 'username' in session:
            username = session['username']
 
            edittitle = request.form['title']
            editcontent = request.form['content']

            conn = connectsql()
            cursor = conn.cursor()
            query = "UPDATE diary SET Title = %s, Content = %s WHERE Num = %s"
            value = (edittitle, editcontent, Num)
            cursor.execute(query, value)
            conn.commit()
            cursor.close()
            conn.close()
    
            return render_template('editSuc.html')
    else:
        if 'username' in session:
            username = session['username']
    
            conn = connectsql()
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            query = "SELECT Title, Content FROM diary WHERE Num = %s"
            value = Num
            cursor.execute(query, value)
            postdata = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('edit.html', data=postdata, logininfo=username)


@app.route('/timeline/delete/<Num>')
def delete(Num):
    conn=connectsql()
    cursor = conn.cursor()
    query = "DELETE FROM diary WHERE Num = %s"
    value = Num
    cursor.execute(query, value)
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('timeline'))


if __name__ == "__main__":
    app.run(debug=True)