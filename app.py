from flask import Flask,render_template,request,url_for,make_response,redirect
from firebase import Firebase
import json
import datetime
import requests

#Url Shortening
header = {
    "Authorization":"bbf116bb1fea464e353f69668d1fedbffed3e885",
    "Content-Type": "application/json"
}
url = 'https://api-ssl.bitly.com/v4/shorten'

def handle_catch(caller, on_exception):
    try:
         return caller()
    except:
         return on_exception

config = {
  "apiKey": "AIzaSyAn1bv1HgddTY8i2KJIUpSjbt2z5VeysIs",
  "authDomain": "iris-web-team.firebaseapp.com",
  "databaseURL": "https://iris-web-team-default-rtdb.firebaseio.com",
  "projectId": "iris-web-team",
  "storageBucket": "iris-web-team.appspot.com",
  "messagingSenderId": "923629246355",
  "appId": "1:923629246355:web:12e9f02d1b6272f39bfa66",
  "measurementId": "G-NJKHGW72RV"
  };

firebase = Firebase(config)
db = firebase.database()
auth = firebase.auth()
app = Flask(__name__)

month_number = {"1":"January","2":"February","3":"March","4":"April","5":"May","6":"June","7":"July","8":"August","9":"September","10":"October","11":"November","12":"December"}

day_number = { "1":"Monday","2":"Tuesday","3":"Wednesday","4":"Thursday","5":"Friday","6":"Saturday","7":"Sunday" }

@app.route("/",methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        uname = request.form.get("username")
        upass = request.form.get("password")
        try:
            user_ = auth.sign_in_with_email_and_password(uname ,upass)
            try:
                all_forms = db.child("Forms").child(request.cookies.get("__user__")).get().val()
            except:
                all_forms  = {}
            resp = make_response(render_template("dashboard.html",forms = all_forms,handle_catch = handle_catch))
            resp.set_cookie('__user__', user_['localId'],max_age=60*60*24)
            resp.set_cookie('__email__', user_['email'],max_age=60*60*24)
            return resp
            

        except Exception  as e:
            # return str(e)
            mes_code = json.loads(e.args[1])['error']['message']
            if(mes_code == "INVALID_PASSWORD"):
                res_code = 500
            elif(mes_code == "EMAIL_NOT_FOUND"):
                res_code = 502
            return render_template("index.html",res_code = res_code,handle_catch = handle_catch)
    
    if request.cookies.get('__user__')is not None and request.cookies.get('__email__') is not None:
        all_forms = db.child("Forms").child(request.cookies.get("__user__")).get().val()
        return render_template("dashboard.html",forms = all_forms,handle_catch = handle_catch)

    return render_template("index.html",handle_catch = handle_catch)

@app.route("/edit/<string:variable_1>",methods=['GET','POST'])
def open_form(variable_1):
    if request.method == 'POST':
        dictionary = json.loads(request.form['main'])
        dictionary['timestamp'] = 'timestamp'
        db.child("Forms").child(request.cookies.get("__user__")).child(variable_1).child("data").set(dictionary)
        return "0"
    form_data_edit= db.child("Forms").child(request.cookies.get("__user__")).child(variable_1).get().val()
    form_data_edit['callback_url'] = f"/edit/{variable_1}"
    form_data_edit['public_url'] = f"/public/{request.cookies.get('__user__')}/{variable_1}"
    return render_template("temp_form.html",form_data =form_data_edit,handle_catch =handle_catch)

@app.route("/edit/<string:variable_1>/change-resp-code",methods=['GET','POST'])
def change_resp_code_form(variable_1):
    if request.method == 'POST':
        if (dict(request.form)['name']=="0"):
            resp_code = dict(request.form)['resp_code']
            db.child("Forms").child(request.cookies.get("__user__")).child(variable_1).update({
                'accepting_response':int(resp_code)
            })
            return resp_code
        elif (dict(request.form)['name']=="1"):
            resp_code = dict(request.form)['resp_code']
            db.child("Forms").child(request.cookies.get("__user__")).child(variable_1).update({
                'admin_notify_new_responses':int(resp_code)
            })
            return resp_code


@app.route("/public/<string:variable_1>/<string:variable_2>",methods=['GET','POST'])
def public_form(variable_1,variable_2):
    if request.method == 'POST':
        if  db.child("Forms").child(variable_1).child(variable_2).child("accepting_response").get().val()==1:
            form_data_public= db.child("Forms").child(variable_1).child(variable_2).child("data").get().val()
            user_entered = dict(request.form)
            set_form_data_public = set(form_data_public)
            set_user_entered = set(user_entered)
            push_dict = {}
            for name in set_form_data_public.intersection(set_user_entered):
                if name == "timestamp":
                    push_dict[name]={
                        'key':form_data_public[name],
                        'resp':user_entered[name],
                    }
                else:
                    push_dict[name]={
                        'key':form_data_public[name]['text'],
                        'resp':user_entered[name],
                    }

            tday = datetime.date.today()
            fmt_date = day_number[str(tday.weekday()+1)]+", "+str(tday.day)+" "+month_number[str(tday.month)]+" "+str(tday.year)+", "+datetime.datetime.today().strftime("%H:%M %p")
            push_dict['timestamp'] ={
                'key':"timestamp",
                'resp':fmt_date
            }
            db.child("Forms").child(variable_1).child(variable_2).child("responses").push(push_dict)
            return render_template("form_submitted.html")
        else:
            return render_template("form_no_responses.html")

    form_data_public= db.child("Forms").child(variable_1).child(variable_2).get().val()
    callback_url = f"/public/{variable_1}/{variable_2}"
    return render_template("form.html",form_data =form_data_public,callback_url=callback_url,handle_catch =handle_catch)

@app.route("/new-form",methods=['GET','POST'])
def new_form():
    if request.method == 'POST' and request.cookies.get("__user__"):
        form_title = request.form.get("form_title") 
        new_form = db.child("Forms").child(request.cookies.get("__user__")).push({
            "form_title":form_title,
            "accepting_response":1,
            "admin_notify_new_responses":0
        })
        # return redirect(url_for('open_form',variable_1 = new_form['name']))
        return redirect(url_for('index'))

@app.route("/signup", methods = ['GET','POST'])
def signup():
    if request.method=='POST':
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            _user_ = auth.create_user_with_email_and_password(username ,password)
            auth.send_email_verification(_user_['idToken'])
            db.child("User_Emails").child(username.split("@")[0]).set({
                "UID":_user_['localId']
            })
            db.child("Users").child(_user_['localId']).set({
                "name":name,    
            })
            return render_template("success.html")
        except Exception as e:
            pass
            return render_template(url_for('index'))
    return render_template("signup.html")

@app.route('/passchange',methods = ['GET','POST'])
def passchange():
    if request.method == 'POST':
        email = request.form.get("pass_change_email")
        auth.send_password_reset_email(email)
        return render_template("passwordchange.html",val = "true")
    return render_template("passwordchange.html",val = "false")

@app.route("/form-delete/<string:form_id>",methods = ['GET','POST'])
def delete(form_id):
    if request.method == 'POST':
        db.child("Forms").child(request.cookies.get("__user__")).child(form_id).remove()
        return redirect(url_for('index'))


@app.route("/edit/<string:variable_1>/shorten-url",methods = ['GET','POST'])
def shorten_url(variable_1):
    if request.method == "POST":
        if request.method == 'POST' and request.cookies.get("__user__"):
            # url_to_short = request.form['public_url_form']
            # url = 'https://api-ssl.bitly.com/v4/shorten'
            # myobj = {
            #     "long_url": url_to_short
            
            
            # }
            # x = requests.post(url, json = myobj,headers=header)
            # short_url = x.link
            # db.child("Forms").child(request.cookies.get("__user__")).child(variable_1).update({
            #      "short-url": short_url
            # })
            # return short_url
            short_url = "Bhai Bhai"
            db.child("Forms").child(request.cookies.get("__user__")).child(variable_1).update({
                 "short-url": short_url
            })
            return short_url


