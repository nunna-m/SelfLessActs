from flask import Flask,jsonify,abort,request
from flask_restful import Api, Resource, reqparse
from flaskext.mysql import MySQL
import json
import datetime
import base64
app = Flask(__name__)
api = Api(app)

mysql = MySQL(app)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'cc'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor =conn.cursor()



@app.route('/api/v1/categories/<categoryName>/acts/size',methods=['GET'])
def ActNum(categoryName):
    cursor.execute('select numberofacts from category where categoryname=%s',categoryName)
    x=cursor.fetchone()

    if(x):
        return jsonify(x),200
    return jsonify({}),204

'''
@app.route('/api/v1/categories/<categoryName>/acts',methods=['GET'])
def actlist(categoryName):

    cursor.execute('select * from category where categoryname=%s',categoryName)
    if cursor.fetchone()==None:
        return "Category not found",405
    cursor.execute('select * from category where categoryname=%s and numberofacts<100',categoryName)
    if cursor.fetchone()==None:
        return "Too many acts ",413
    cursor.execute('select * from act where category in (select categoryname from  category where categoryname=%s and numberofacts<100)',categoryName)
    info=cursor.fetchall()
    if info:
        return jsonify(info),200
    #if info:
    else:
        return "Error",405


'''



app.run(debug=True)
