from flask import Flask
import flask
from flask import request, redirect
from flask import jsonify
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask_restful import Api, Resource, reqparse
import json, requests
import string
import datetime
import base64
import os
import re
application = Flask(__name__)
app = application
CORS(app,support_credentials=True,resources={r"/*":{"origins":"http://18.210.123.131"}})
api = Api(app)
permitted_get=["api/v1/act","api/v1/category","api/v1/allacts","api/v1/categories/acts","api/v1/categories","api/v1/_count","api/v1/acts/count"]
permitted_post=["api/v1/acts","api/v1/categories","api/v1/acts/upvote"]
permitted_delete = ["api/v1/_count"]
@app.route('/<path:text>',methods=['GET','POST','DELETE','PUT'])
def apis(text):
        port=8000
        host='localhost'
        if flask.request.method=='GET':
                x = re.match("^api[/]v1[/]categories[/].*[/]acts$", text)
                y = re.match("^api[/]v1[/]categories[/].*[/]acts[/]size$", text)
                if(x!=None or y!=None or text in permitted_get):
                        return redirect('http://'+str(host)+':'+str(port)+'/'+text)
        if flask.request.method=='POST':
                if(text in permitted_post):
                        return redirect('http://'+str(host)+':'+str(port)+'/'+text,code=307)
        if flask.request.method=='DELETE':
                x = re.match("^api[/]v1[/]categories[/].*$",text)
                y = re.match("^api[/]v1[/]acts[/].*$",text)
                if(x!=None or y!=None or text in permitted_delete):
                        return redirect('http://'+str(host)+':'+str(port)+'/'+text,code=307)
    #receive request with path
    #analyze path and redirect only if path is of form /act
    #maintain global variable roundrobinpointer
app.run(host="0.0.0.0",port=3000,debug=True)
conn.close()