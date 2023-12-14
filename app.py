from flask import (
    Flask, render_template, jsonify, request, session, redirect, url_for)
from pymongo import MongoClient
import jwt
from datetime import datetime, timedelta
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.secret_key = 'EVENTIFY'

MONGODB_CONNECTION_STRING = 'mongodb+srv://20051204052:l8YdBYlzNSheWHSf@unesa.sit4ohz.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.db_eventify

TOKEN_KEY ="mytoken"

@app.route('/')
def home():
    events_collection = db.events
    events = events_collection.find()
    return render_template('index.html', events=events)

@app.route("/", methods=["GET"])
def home():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, app.secret_key, algorithms=["HS256"])

        user_info = db.events.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="Your token has expired"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="There was problem logging you in"))


@app.route("/login", methods=["GET"])
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

@app.route("/sign_in", methods=["POST"])
def sign_in():
    # Sign in
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.events.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "id": username_receive,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, app.secret_key, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               
        "password": password_hash,                                  
        "profile_name": username_receive,                           
        "profile_pic": "",                                          
        "profile_pic_real": "profile_pics/profile_placeholder.png", 
        "profile_info": ""                                          
    }
    db.events.insert_one(doc)
    
    return jsonify({'result': 'success'})


@app.route("/sign_up/check_dup", methods=["POST"])
def check_dup():
    # ID we should check whether or not the id is already taken
    username_receive = request.form.get('username_give')
    exists = bool(db.events.find_one({'username': username_receive}))
    return jsonify({"result": "success", "exists": exists})

@app.route('/create_event', methods=['POST'])
def create_event():
    event = request.form.get('event')
    kategori = request.form.get('kategori')
    deskripsi = request.form.get('deskripsi')
    link_pendaftaran = request.form.get('linkPendaftaran')
    contact_info = request.form.get('contactInfo')
    deadline = request.form.get('deadline')
    foto = request.files['foto']

    # Simpan data ke MongoDB
    events_collection = db.events
    data_event = {
        'event': event,
        'kategori': kategori,
        'deskripsi': deskripsi,
        'link_pendaftaran': link_pendaftaran,
        'contact_info': contact_info,
        'deadline': deadline,
        'foto': foto,
    }
    events_collection.insert_one(data_event)

    return jsonify({'success': True, 'message': 'Event berhasil ditambahkan!'})

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
