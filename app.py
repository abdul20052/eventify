from flask import (
    Flask, render_template, jsonify, request, session, redirect, url_for)
from pymongo import MongoClient
from bson.objectid import ObjectId
import base64
import jwt
from datetime import datetime, timedelta
import hashlib
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'EVENTIFY'

MONGODB_CONNECTION_STRING = 'mongodb+srv://20051204052:l8YdBYlzNSheWHSf@unesa.sit4ohz.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_CONNECTION_STRING)

db = client.db_eventify

TOKEN_KEY ="mytoken"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login', msg='You need to login first'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/create_event')
@login_required
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
    foto_receive = request.form.get('foto_give')
    username_receive = session['username']

    # Simpan data ke MongoDB
    data_event = {
        "event": event_receive,
        "organizer": organizer_receive,
        "kategori": kategori_receive,
        "deskripsi": deskripsi_receive,
        "link_pendaftaran": link_receive,
        "deadline": deadline_receive,
        "foto": foto_receive,
        "username": username_receive,
    }
    db.events.insert_one(data_event)
    return jsonify({
        "result": "success", 
        "message": "Event berhasil ditambahkan!"
    })

from flask import render_template

@app.route('/my_events', methods=['GET'])
@login_required
def get_my_events():
    username = session['username']
    events = db.events.find({'username': username})

    events_list = []
    for event in events:
        events_list.append({
            '_id': str(event['_id']),
            'event': event['event'],
            'organizer': event['organizer'],
            'kategori': event['kategori'],
            'deskripsi': event['deskripsi'],
            'link_pendaftaran': event['link_pendaftaran'],
            'deadline': event['deadline'],
            'foto': event['foto'],
            'views': event.get('views', 0)
        })

    return render_template('my_events.html', events=events_list)

@app.route('/get_events', methods=['GET'])
def get_events():
    events = db.events.find()

    events_list = []
    for event in events:
        events_list.append({
            '_id': str(event['_id']),
            'event': event['event'],
            'organizer': event['organizer'],
            'kategori': event['kategori'],
            'deskripsi': event['deskripsi'],
            'link_pendaftaran': event['link_pendaftaran'],
            'deadline': event['deadline'],
            'foto': event['foto'],
            'views': event.get('views', 0)
        })

    return jsonify({'events': events_list})

@app.route('/get_event/<event_id>', methods=['GET'])
def get_event(event_id):
    event = db.events.find_one({'_id': ObjectId(event_id)})
    event['_id'] = str(event['_id'])
    return jsonify(event)

@app.route('/event/<event_id>')
@login_required
def detail_event(event_id):
    event = db.events.find_one({'_id': ObjectId(event_id)})
    return render_template('event_detail.html', event=event)

@app.route('/')
def home():
    events_collection = db.events
    events = events_collection.find()
    return render_template('index.html', events=events, logged_in='username' in session)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username_receive = request.form["username_give"]
        # Lakukan autentikasi dan set session jika berhasil
        session['username'] = username_receive
        return redirect(url_for('home'))
    return render_template('login.html', msg=request.args.get("msg"))

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route("/sign_in", methods=["POST"])
def sign_in():
    # Sign in
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.users.find_one(
        {
            "username": username_receive,
            "password": pw_hash,
        }
    )
    if result:
        session['username'] = username_receive
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
    db.users.insert_one(doc)
    
    return jsonify({'result': 'success'})


@app.route('/event/<event_id>/views', methods=['POST'])
def update_views(event_id):
    event = db.events.find_one({'_id': ObjectId(event_id)})
    if event.get('views'):
        views = event['views'] + 1
    else:
        views = 1
    db.events.update_one({'_id': ObjectId(event_id)}, {'$set': {'views': views}})
    return jsonify({'msg': 'success'})


@app.route('/edit', methods=['PATCH'])
def edit_event():
    event_id = request.form.get('event_id_give')
    event_receive = request.form.get('event_give')
    organizer_receive = request.form.get('organizer_give')
    kategori_receive = request.form.get('kategori_give')
    deskripsi_receive = request.form.get('deskripsi_give')
    link_receive = request.form.get('link_give')
    deadline_receive = request.form.get('deadline_give')
    foto_receive = request.form.get('foto_give')

    db.events.update_one({'_id': ObjectId(event_id)}, {'$set': {
        'event': event_receive,
        'organizer': organizer_receive,
        'kategori': kategori_receive,
        'deskripsi': deskripsi_receive,
        'link_pendaftaran': link_receive,
        'deadline': deadline_receive,
        'foto': foto_receive
    }})

    return jsonify({'message': 'Event berhasil diubah!'})

@app.route('/edit_event')
def get_edit_event():
    return render_template('edit_event.html')

@app.route('/delete_event', methods=['POST'])
def delete_event():
    event_id = request.form.get('_id')
    db.events.delete_one({'_id': ObjectId(event_id)})
    return jsonify({'message': 'Event berhasil dihapus!'})

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
