from app import app
from datetime import datetime

import os
import pymysql
import pylint
import time

from flask import session, url_for
from flask import render_template
from flask import request, redirect
from flask import jsonify, make_response
from flask import Flask, Response
from werkzeug.utils import secure_filename
from flask import send_file, send_from_directory, safe_join, abort
from flask import flash
from flask import stream_with_context

class Database:
    def __init__(self, user, port):
        self._user = user
        self._port = port

    def get_local_db(self):
        db = pymysql.connect(host='localhost',
                        port=self._port,
                        user=self._user,
                        passwd='cd101368@',
                        db='hug',
                        charset='utf8')
        cursor = db.cursor()
        return db, cursor

    def get_db(self):
        db = pymysql.connect(host='34.64.149.185',
                        port=self._port,
                        user=self._user,
                        passwd='',
                        db='hugs',
                        charset='utf8')
        cursor = db.cursor()
        return db, cursor
    

#configuration image
app.config["IMAGE_UPLOADS"] = "/static/img/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

#configuration audio
app.config["AUDIO_UPLOADS"] = "/static/audio/uploads"
app.config["ALLOWED_AUDIO_EXTENSIONS"] = ["MP3", "WAV", "WMA", "AIFF", "ALAC"]

#configuration login
app.config["SECRET_KEY"] = 'n1otDX895NuHB51rv6paUA'
    
#container
user_session_container = dict()

#database instance
user_database = Database('root', 3306)

@app.route("/")
def index():
    return render_template("public/index.html", session=session.get("USERNAME"))

@app.route("/lyrics")
def lyrics():
    return render_template("public/lyrics.html", session=session.get("USERNAME"))

@app.route("/makeMusic")
def makeMusic():
    return render_template("public/makeMusic.html", session=session.get("USERNAME"))

@app.route("/making")
def making():
    return render_template("public/making.html", session=session.get("USERNAME"))

@app.route("/musicList")
def musicList():
    sql = """select * from musiclist;"""
    result = sql_runner(sql)
    print(result)
    end = len(result)
    return render_template("public/musicList.html", session=session.get("USERNAME"), music=result, end=end)

@app.route("/musicListHigh")
def musicListHigh():
    return render_template("public/musicListHigh.html", session=session.get("USERNAME"))

@app.route("/musicListLow")
def musicListLow():
    return render_template("public/musicListLow.html", session=session.get("USERNAME"))

@app.route("/myMusicList")
def myMusicList():
    if not session.get("USERNAME") is None:
        return render_template("public/myMusicList.html", session=session.get("USERNAME"))
    else:
        flash("로그인이 필요합니다.")
        return redirect(request.url.replace('myMusicList','login'))

@app.route("/playList")
def playList():
    if not session.get("USERNAME") is None:
        sql = """select * from playlist;"""
        result = sql_runner(sql)
        end = len(result)
        return render_template("public/playList.html", session=session.get("USERNAME"), playlist=result, end=end)
    else:
        flash("로그인이 필요합니다.")
        return redirect(request.url.replace('playList','login'))

@app.route("/playList/<list_name>")
def playList_detail(list_name):
    if not session.get("USERNAME") is None:
        sql = f"select * from playlist where p_name='{list_name}';"
        playlist_name = sql_runner(sql)[0][1]

        sql = f"select * from playlist_music where pm_id = (select p_id from playlist where p_name='{playlist_name}');"
        final_result = sql_runner(sql)
        end = len(final_result)
        return render_template("public/playListMusic.html", session=session.get("USERNAME"), name=playlist_name ,playlist=final_result, end=end)
    else:
        flash("로그인이 필요합니다.")
        return redirect(request.url.replace('playList','login'))

def sql_runner(sql):
    db, cursor = user_database.get_db()
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

@app.route("/playListMusic")
def playListMusic():   
    return render_template("public/playListMusic.html", session=session.get("USERNAME"))

@app.route("/select")
def select():
    return render_template("public/select.html", session=session.get("USERNAME"))

@app.route("/signup")
def signup():
    return render_template("public/signup.html", session=session.get("USERNAME"))

@app.route("/terms")
def terms():
    return render_template("public/Hugs.html", session=session.get("USERNAME"))

@app.route("/upload", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":

        if request.files:
            if "filesize" in request.cookies:
                if not allowed_image_filesize(request.cookies["filesize"]):
                    print("Filesize exceeded maximum limit")
                    return redirect(request.url)

                image = request.files["image"]

                if image.filename == "":
                    print("No filename")
                    return redirect(request.url)
                if allowed_image(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config["IMAGE_UPLOADS"], filename))
                    print("Image saved")
                    return redirect(request.url)
                else:
                    print("That file extension is not allowed")
                    return redirect(request.url)

    return render_template("public/upload.html", session=session.get("USERNAME"))

@app.route("/upload-audio", methods=["GET", "POST"])
def upload_audio():
    return render_template("public/upload.html")

@app.route("/streaming")
def streaming_main_page():
    return render_template("public/stream.html", session=session.get("USERNAME"))
    
@app.route("/musicList/<song_name>")
def streamwav(song_name):
    def generate():
        with open(f"app/static/audio/uploads/{song_name}.mp3", "rb") as song:
            data = song.read(1024)
            while data:
                yield data
                data = song.read(1024)
    return Response(stream_with_context(generate()), mimetype="audio/x-wav")

@app.route("/about")
def about():
    return render_template('public/about.html', session=session.get("USERNAME"))

@app.route("/all")
def all():
    sql = """select * from accounts;"""
    result = sql_runner(sql)
    return "all members : " + str(result)
    
@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    db, cursor = user_database.get_db()

    if request.method == "POST":
        req = request.form
        username = req["username"]
        email = req["email"]
        password = req["password"]
        conf_password = req["conf_password"]

        print(password+' '+conf_password)
        # empty list -> full list has members of number of error
        missing = list()

        for key, value in req.items():
            if value == "":
                missing.append(key)

        # 1. check a empty field 2.checking mismatched case of password confirmation
        if missing:
            flash(f"다음이 입력되지 않았습니다 : {', '.join(missing)}")
            return redirect(request.url)
        elif password != conf_password:
            flash("패스워드가 일치하지 않습니다.")
            return redirect(request.url)
        elif not len(password) >= 6:
            flash("비밀번호는 최소 6자 이상이여야 합니다.")
            return redirect(request.url)
        
        # test all of validation test of form
        sql = """INSERT INTO accounts VALUES('%s', '%s' 
        ,'%s') """ % (username, email, password) 

        cursor.execute(sql)
        db.commit()
        db.close()
        
        flash("Account created!")
        return redirect(request.url.replace('sign-up','login'))

    return render_template("public/signup.html", session=session.get("USERNAME"))

@app.route("/login", methods=["GET","POST"])
def login():
    db, cursor = user_database.get_db()
    print("session: " + str(session.get("USERNAME")))
    if not session.get("USERNAME") is None:
        return redirect(request.url.replace('login','profile'))
    else:
        if request.method == "POST":
            req = request.form
            email = req.get("email")
            password = req.get("password")

            sql = """SELECT * FROM accounts WHERE email='%s'
            """ % (email) 
            cursor.execute(sql)
            result = cursor.fetchall()
            print("username: " + str(result[0][0]))

            if result:
                if str(result[0][2]) == str(password):
                    print('로그인 성공')
                    container(result[0])
                    session["USERNAME"] = str(result[0][0])
                    db.close()
                    print("container: "+str(user_session_container[session["USERNAME"]]))
                    return render_template("public/index.html", user=str(user_session_container[session["USERNAME"]]), status='Logout', session=session.get("USERNAME"))
                else:
                    flash("잘못된 비밀번호입니다.")
                    return redirect(request.url)
            else:
                flash("존재하지 않는 사용자입니다.")
                return redirect(request.url)

    return render_template("public/login.html", session=session.get("USERNAME"))

@app.route("/logout")
def logout():
    session.pop("USERNAME", None)
    return redirect(url_for("index"))

@app.route("/profile")
def profile():
    if not session.get("USERNAME") is None:
        print('checkpoint A')
        return render_template("public/profile.html", user=str(session.get("USERNAME")), status='Logout')
    else:
        print('need login')
        flash("로그인이 필요합니다", "warning")
        print('checkpoint B')
        return redirect(url_for("login"))

def container(user):
    user_session_container[user[0]] = user

def allowed_image(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def allowed_image_filesize(filesize):
    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False
