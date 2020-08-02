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


@app.route('/signup',methods=['POST','GET'])
def Signup():

    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'uname':request.form['signupusername']})
        existing_email = users.find_one({'email':request.form['signupemail']})

        if (existing_user is None) and (existing_email is None):
            hashpass = bcrypt.hashpw(request.form['signuppassword'].encode('utf-8'),bcrypt.gensalt())
            users.insert({'uname': request.form['signupusername'],'email': request.form['signupemail'],
                            'contact': request.form['signupphone'], 'password' : hashpass,'utype':"u"})
            # session['username'] = request.form['signupusername']
            flash("Successfully Signed up")
            return redirect(url_for('home'))

        elif (existing_email is None) and (existing_user is not None):
            flash("That Username Already Exists!")
            return redirect(url_for('Signup'))

        elif (existing_user is None) and (existing_email is not None) :
            flash('Email is Already Taken')
            return redirect(url_for('Signup'))

        flash('User Already Exists')
        return redirect(url_for('Signup'))

    return render_template('signup.html')


@app.route('/details')
def read_more():
    return render_template('details.html')


@app.route('/details')
def read_more():
    return render_template('details.html')


@app.route('/adminDashboard')
def adminDashboard():
    if 'username' in session:
        username = session['username']

        return redirect(url_for('admin_display'))

    return redirect(url_for('login'))


@app.route('/admin_display')
def admin_display():
    if 'username' in session:
        username = session['username']

        images = mongo.db.user_images.find({'isVerified':0})
        user_count = mongo.db.users.find().count()
        grievances_count = mongo.db.user_images.find().count()


        return render_template('admin_display.html', value_username = username, dbentry = images, u_count = user_count, g_count = grievances_count)
    else:
        return redirect(url_for('login'))


@app.route('/user', methods=['GET','POST'])
def upload_image():
    if 'username' in session:
        username = session['username']
        return render_template('user.html',value_username= username)
    else:
        return redirect(url_for('login'))


@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@app.route('/sign_out')
def sign_out():
    if "username" in session:
        flash("Successfully Logged Out!")
        session.pop('username')
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.secret_key = 'merasecret'
    app.run(debug = True)
