from flask import (
    Flask, render_template, jsonify, request, session, redirect, url_for)
from pymongo import MongoClient
import base64
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

@app.route('/create_event')
def create_event():
    return render_template('create_event.html')

@app.template_filter('formatdate')
def format_date(value, format='%d %B %Y'):
    return datetime.strptime(value, '%Y-%m-%d').strftime(format)


@app.route("/posting", methods=["POST"])
def posting():
    event_receive = request.form.get('event_give')
    organizer_receive = request.form.get('organizer_give')
    kategori_receive = request.form.get('kategori_give')
    deskripsi_receive = request.form.get('deskripsi_give')
    link_receive = request.form.get('link_give')
    deadline_receive = request.form.get('deadline_give')

    if "foto_give" in request.files:
            file = request.files['foto_give']
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            # Ganti spasi dengan underscore dalam nama file
            filename= event_receive.replace(" ", "_")
            file_path = f"event_pics/{filename}.{extension}"
            file.save("./static/" + file_path)
    
    # Simpan data ke MongoDB
    data_event = {
        "event": event_receive,
        "organizer": organizer_receive,
        "kategori": kategori_receive,
        "deskripsi": deskripsi_receive,
        "link_pendaftaran": link_receive,
        "deadline": deadline_receive,
        "foto": file_path,
    }
    db.events.insert_one(data_event)
    return jsonify({
        "result": "success", 
        "message": "Event berhasil ditambahkan!"
    })

@app.route('/get_events', methods=['GET'])
def get_events():
    events = db.events.find()

    events_list = []
    for event in events:
        events_list.append({
            'event': event['event'],
            'organizer': event['organizer'],
            'kategori': event['kategori'],
            'deskripsi': event['deskripsi'],
            'link_pendaftaran': event['link_pendaftaran'],
            'deadline': event['deadline'],
            'foto': event['foto'],
        })

    return jsonify({'events': events_list})

@app.route('/')
def home():
    events_collection = db.events
    events = events_collection.find()
    return render_template('index.html', events=events)


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


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
