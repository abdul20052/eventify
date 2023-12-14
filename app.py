from pymongo import MongoClient
from flask import Flask, redirect, url_for, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'EVENTIFY'

MONGODB_CONNECTION_STRING = 'mongodb+srv://20051204052:l8YdBYlzNSheWHSf@unesa.sit4ohz.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.db_eventify

@app.route('/')
def home():
    events_collection = db.events
    events = events_collection.find()
    return render_template('index.html', events=events)

@app.route('/create_event')
def create_event():
    return render_template('create_event.html')

@app.route("/posting", methods=["POST"])
def posting():
    event_receive = request.form.get('event_give')
    organizer_receive = request.form.get('organizer_give')
    kategori_receive = request.form.get('kategori_give')
    deskripsi_receive = request.form.get('deskripsi_give')
    link_receive = request.form.get('link_give')
    deadline_receive = request.form.get('deadline_give')
    hashtag1_receive = request.form.get('hashtag1_give')
    hashtag2_receive = request.form.get('hashtag2_give')

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
        "hashtag1": hashtag1_receive,
        "hashtag2": hashtag2_receive,
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
            'hashtag1': event['hashtag1'],
            'hashtag2': event['hashtag2'],
            'foto': event['foto'],
        })

    return jsonify({'events': events_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)