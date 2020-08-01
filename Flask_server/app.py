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


@app.route('/login',methods=['POST','GET'])
def login():
    if 'username' in session:
        return redirect(url_for('uDashboard'))

    if request.method == 'POST' :
        users = mongo.db.users
        utype = request.form['Login']
        login_user = users.find_one({'email' : request.form['email']})

        if login_user :
            if bcrypt.hashpw(request.form['password'].encode('utf-8'),login_user['password']) == login_user['password']:
                if login_user['utype'] != utype:
                    flash("Not a User/Admin")
                    return redirect(url_for('login'))

                if login_user['utype'] == "u":
                    session['username'] = login_user['uname']
                    return redirect(url_for('uDashboard',utype = utype))
                else :
                    session['username'] = login_user['uname']
                    return redirect(url_for('adminDashboard',utype = utype))


        flash('Invalid Email/Password combination')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/details')
def read_more():
    return render_template('details.html')
