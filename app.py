from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url or ('youtube' not in url and 'youtu.be' 
