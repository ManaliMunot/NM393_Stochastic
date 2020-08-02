from flask import Flask, render_template, request, redirect, session, url_for, jsonify,flash
from flask_bootstrap import Bootstrap
from bson import ObjectId # For ObjectId to work
from key_extract.keyword_extractor import *
import os
from caption_gen.get_caption import *
# from flask_paginate import Pagination, get_page_parameter
import bcrypt
from werkzeug.utils import secure_filename
# from trafic_sign.classifier import *
from flask_pymongo import PyMongo

UPLOAD_FOLDER = './uploads'
path = 'E:/SIH/NM393/NM393_Stochastic/Flask_server/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','ppm'}

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/db_images"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


mongo = PyMongo(app)
Bootstrap(app)
#--------------------------------------------------------------------------------

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




#--------------------------------------------------------------------------------

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



@app.route('/verify', methods=["POST"])
def verify():
    oid = request.form['id']
    # isVerify = int(request.values.get('name'))
    mongo.db.user_images.update({"_id" : ObjectId(oid)}, {"$set": {'isVerified':1}}, upsert=True)

    return jsonify({'result' : 'success'})

@app.route('/verify_not', methods=["POST"])
def verify_not():
    oid = request.form['id']
    # isVerify = int(request.values.get('name'))
    mongo.db.user_images.update({"_id" : ObjectId(oid)}, {"$set": {'isVerified':-1}}, upsert=True)

    return jsonify({'result' : 'success'})





@app.route('/user', methods=['GET','POST'])
def upload_image():
    if 'username' in session:
        username = session['username']
        return render_template('user.html',value_username= username)
    else:
        return redirect(url_for('login'))


@app.route('/to_db',methods=['POST'])
def to_db():
    if 'userImage' in request.files:
        imgDesc = request.form["description"]
        imgCat = request.form["category"]
        file = request.files['userImage']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            caption_dict = run(path+filename)
            os.remove(path+filename)

            captions = []
            for value in caption_dict.values():
                captions.append(value[0])

        extractor = KeywordExtractor()
        extractor.analyze(imgDesc, candidate_pos = ['NOUN', 'PROPN','VERB'], window_size=4, lower=False)
        highlights = extractor.get_keywords(12)

        mongo.save_file(filename, file)
        mongo.db.user_images.insert_one({'uname':session['username'], 'userImage_name': filename,'imgDescription' : imgDesc ,'imgCategory' : imgCat,
                                            'isValidated':0,'isVerified':0, 'captions': captions,'key_highlight':highlights})

        flash("Image Uploaded")
        return redirect(url_for('upload_image'))

@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)



@app.route('/uDashboard')
def uDashboard():
    if 'username' in session:
        username = session['username']
        return render_template('user_main.html',value_username= username)
    else:
        return redirect(url_for('login'))


@app.route('/display')
def display():
    if 'username' in session:
        username = session['username']

        images = mongo.db.user_images.find({'uname':username})

        return render_template('display.html', value_username = username, dbentry = images)
    else:
        return redirect(url_for('login'))


@app.route('/resubmit',methods=['POST','GET'])
def user_resubmit():

    if 'username' in session:
        username = session['username']
        id=request.values.get("_id")
        get_detail=mongo.db.user_images.find_one({"_id":ObjectId(id)})

        return render_template('user_resubmit.html',value_username= username, image = get_detail)


    return redirect(url_for('login'))



@app.route('/reupload_grievances', methods=['POST'])
def reupload_grievances():
    if 'username' in session:

        if 'userImage' in request.files:
            userImage = request.files['userImage']
            imgName = secure_filename(userImage.filename)
            imgID = request.values.get("_id")
            imgDesc = request.values.get("description")
            imgCat = request.values.get("category")
            mongo.save_file(imgName, userImage)

            extractor = KeywordExtractor()
            extractor.analyze(imgDesc, candidate_pos = ['NOUN', 'PROPN','VERB'], window_size=4, lower=False)
            highlights = extractor.get_keywords(12)

            mongo.db.user_images.update({"_id" : ObjectId(imgID)}, {"$set": {'userImage_name': imgName,'imgDescription' : imgDesc ,
            'imgCategory' : imgCat,'isVerified':0, 'isValidated':1, 'key_highlight':highlights}}, upsert=True)
            return redirect(url_for('display'))



#  Done
@app.route('/sign_out')
def sign_out():
    if "username" in session:
        flash("Successfully Logged Out!")
        session.pop('username')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.secret_key = 'merasecret'
    app.run(debug = True)
