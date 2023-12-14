from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, session
import base64
from datetime import datetime

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

@app.route('/create_event', methods=['GET'])
def create_event_page():
    return render_template('create_event.html')

@app.template_filter('formatdate')
def format_date(value, format='%d %B %Y'):
    return datetime.strptime(value, '%Y-%m-%d').strftime(format)

@app.route('/create_event', methods=['POST'])
def create_event():
    event = request.form.get('event')
    kategori = request.form.get('kategori')
    deskripsi = request.form.get('deskripsi')
    link_pendaftaran = request.form.get('linkPendaftaran')
    contact_info = request.form.get('contactInfo')
    deadline = request.form.get('deadline')
    foto = request.form.get('foto')

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


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)