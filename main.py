

from flask import Flask,render_template,request,make_response,redirect,url_for
import random as rd
from datetime import date
app = Flask(__name__)
month_number = {"1":"January","2":"February","3":"March","4":"April","5":"May","6":"June","7":"July","8":"August","9":"September","10":"October","11":"November","12":"December"}
def rand_pass(len):
    pass_data = "qwertyuiopasdfgjklzxcvbnm1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
    password = "".join(rd.sample(pass_data, len))
    return password


@app.route('/',methods= ['GET','POST'])
def start():
    if (request.cookies.get('__user__')==None):
        uid_for_user = rand_pass(10)
        resp = make_response(render_template('index.html',UID =uid_for_user))
        resp.set_cookie('__user__',uid_for_user,max_age = 60*60*24)
        resp.set_cookie('__registered__',"0",max_age = 60*60*24)
        return resp
    else:
        uid_for_user = request.cookies.get('__user__')
        return render_template('index.html',UID =uid_for_user)


@app.route('/mess',methods = ['GET','POST'])
def mess():
    print(f"request.cookies.get('__registered__') = {request.cookies.get('__registered__')}")
    if (request.cookies.get('__registered__') == "0"):
        return render_template('mess_detail.html',resp_code = 540)
    else:
        return render_template('mess_detail.html',resp_code = 541)


@app.route('/mess/dues',methods = ['GET','POST'])
def mess_dues():
    return render_template('mess_detail_dues.html')

@app.route('/mess/card',methods = ['GET','POST'])
def mess_card():
    if(request.cookies.get('__registered__')=='0'):
        return redirect(url_for('start'))
    return render_template('mess_card.html',mess_card_number=request.cookies.get('__mess_card_number__'),mess_name =request.cookies.get('__mess_name__'),date = request.cookies.get('__issuedate__'))

@app.route('/mess/change',methods = ['GET','POST'])
def mess_change():
    return render_template('mess_detail_change.html')

@app.route('/mess/invoice',methods = ['GET','POST'])
def mess_invoice():
    if(request.cookies.get('__registered__')=='0'):
        return redirect(url_for('start'))
    else:
        global today,mess_card_number
        today = date.today()
        mess_card_number = rd.randint(10000, 99999) 
        resp = make_response(render_template('mess_invoice.html'))
        resp.set_cookie('__issuedate__',str(today),max_age = 60*60*24)
        resp.set_cookie('__mess_card_number__',str(mess_card_number),max_age = 60*60*24)
        return resp

@app.route('/mess/payments',methods = ['POST'])             
def mess_payments():
    if request.method == 'POST':
        resp__ = make_response(redirect(url_for('mess_invoice')))
        resp__.set_cookie('__registered__',"1",max_age = 60*60*24)
        return resp__


@app.route('/mess/registration',methods = ['GET','POST'])
def mess_registration():
    if request.method == 'POST':
        global mess_name
        mess_name = request.form.get('Mess_Name')
        resp_ = make_response(render_template('mess_detail_payment.html',mess_name = mess_name))
        resp_.set_cookie('__mess_name__',mess_name)
        return resp_
    return render_template('mess_detail_registration.html')

@app.route('/hostel',methods = ['GET','POST'])
def hostel():
    return render_template('hostel.html')

@app.route('/gyan',methods = ['GET','POST'])
def gyan():
    return render_template('mess_detail.html')

if __name__ == '__main__':
    app.run(debug = True)