from flask import Flask
import flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask_restful import Api, Resource, reqparse
import json
import string
import datetime
import base64
app = Flask(__name__)
CORS(app)
api = Api(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'cc'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor =conn.cursor()
names = ('actId','username','timestamp','caption','upvotes','imgB64')


@app.route('/api/v1/users',methods=['GET'])
def UserList():
    cursor=conn.cursor()
    conn.commit()
    cursor.execute("select username from user")
    conn.commit()
    allusers=cursor.fetchall()
    print(allusers)
    if(allusers):
        return jsonify(allusers),200
    else:
        return jsonify({}),204
