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



#configuration image
app.config["IMAGE_UPLOADS"] = "C:/hugs/app/static/img/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

#configuration audio
app.config["AUDIO_UPLOADS"] = "C:/hugs/app/static/audio/uploads"
app.config["ALLOWED_AUDIO_EXTENSIONS"] = ["MP3", "WAV", "WMA", "AIFF", "ALAC"]

#configuration login
app.config["SECRET_KEY"] = 'n1otDX895NuHB51rv6paUA'
    
#database
def get_db():
    db = pymysql.connect(host='localhost',
                        port=3306,
                        user='root',
                        passwd='',
                        db='hugs',
                        charset='utf8')
    cursor = db.cursor()
    return db, cursor

# mocking object
users = {
    "Dawon": {
        "username": "Dawon",
        "email": "cd941568@gmail.com",
        "password": "cd1234",
        "bio": "CTO, Google LLC",
        "twitter_handle": "@dawon"
    }
}


@app.route("/")
def index():
    return render_template("public/index.html", session=session.get("USERNAME"))

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
    

@app.route("/streaming/<song_name>")
def streamwav(song_name):
    def generate():
        with open(f"app/static/audio/uploads/{song_name}.wav", "rb") as song:
            data = song.read(1024)
            while data:
                yield data
                data = song.read(1024)
    return Response(stream_with_context(generate()), mimetype="audio/x-wav")


@app.route("/about")
def about():
    return render_template('public/about.html')


@app.route("/all")
def all():
    db, cursor = get_db()
    sql = """select * from accounts;"""
    cursor.execute(sql)
    result = cursor.fetchall()
    return "all members : " + str(result)
    

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    db, cursor = get_db()

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
            flash(f"다음이 입력되지 않았습니다 : {', '.join(missing)}", "warning")
            return redirect(request.url)
        elif password != conf_password:
            flash("패스워드가 일치하지 않습니다.", "warning")
            return redirect(request.url)
        elif not len(password) >= 6:
            flash("비밀번호는 최소 6자 이상이여야 합니다.", "warning")
            return redirect(request.url)
        
        # test all of validation test of form
        sql = """INSERT INTO accounts VALUES('%s', '%s' 
        ,'%s') """ % (username, email, password) 

        cursor.execute(sql)
        db.commit()
        db.close()
        
        flash("Account created!", "success")
        return redirect(request.url.replace('sign-up','login'))

    return render_template("public/sign_up.html", session=session.get("USERNAME"))


@app.route("/login", methods=["GET","POST"])
def login():
    db, cursor = get_db()
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
            print(result)

            if result:
                if str(result[0][2]) == str(password):
                    container(result[0])
                    print("[0][0] : ", result[0][0])
                    session["USERNAME"] = str(result[0][0])
                    db.close()
                    return redirect(url_for('profile'))
                else:
                    flash("잘못된 비밀번호입니다.", "warning")
                    return redirect(request.url)
            else:
                flash("존재하지 않는 사용자명입니다.", "warning")
                return redirect(request.url)

    return render_template("public/login.html", session=session.get("USERNAME"))

user_container = dict()
def container(user):
    user_container[user[0]] = user

@app.route("/profile")
def profile():
    if not session.get("USERNAME") is None:
        username = session.get("USERNAME")
        return render_template("public/profile.html", user=user_container[username], status='Logout')
    else:
        flash("로그인이 필요합니다", "warning")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("USERNAME", None)
    return redirect(url_for("index"))


@app.route("/json", methods=["POST"])
def json_example():
    if request.is_json:
        req = request.get_json()
        response_body = {
            "message": "JSON received!",
            "sender": req.get("name")
        }
        res = make_response(jsonify(response_body), 200)
        return res
    else:
        return make_response(jsonify({"message": "Request body must be JSON"}), 400)


@app.route("/query")
def query():
    if request.args:
        args = request.args
        serialized = ", ".join(f"{k}: {v}" for k, v in args.items())
        return f"(Query) {serialized}", 200
    else:
        return "No query string received", 200 


@app.route("/guestbook")
def guestbook():
    return render_template("public/guestbook.html")


@app.route("/guestbook/create-entry", methods=["POST"])
def create_entry():
    req = request.get_json()
    print(req)
    res = make_response(jsonify(req), 200)
    return res

