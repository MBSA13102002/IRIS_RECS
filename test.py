from flask import Flask,render_template,request,url_for,make_response,redirect
from firebase import Firebase

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
kk = {1: [2, 6], 3: [4, 7]}
db.child("Mbsa").push(kk)