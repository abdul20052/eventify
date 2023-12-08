import requests
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, session
app = Flask(__name__)
app.secret_key = 'EVENTIFY'

# MONGODB_CONNECTION_STRING = "SECRET"
# client = MongoClient(MONGODB_CONNECTION_STRING)
# db = client.dblearningx

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)