from flask import Flask, render_template, request, redirect, session, url_for, jsonify,flash
from flask_bootstrap import Bootstrap
import os
from werkzeug.utils import secure_filename
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/db_images"


mongo = PyMongo(app)
Bootstrap(app)



@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('uDashboard'))

    return render_template('index.html')
