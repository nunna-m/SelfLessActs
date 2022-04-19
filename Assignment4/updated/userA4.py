from flask import Flask
import flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask_restful import Api, Resource, reqparse
import json, requests
import string
import datetime
import base64
import os
application = Flask(__name__)
app = application
CORS(app,support_credentials=True)
api = Api(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'cc'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
#conn = mysql.connect()
#cursor =conn.cursor()
names = ('actId','username','timestamp','caption','upvotes','imgB64')
names2 = ('actId','username','timestamp','caption','upvotes','imgB64','category')

fd=open('check.txt',"w")
fd.write('0')
fd.close()
conn = mysql.connect()
cursor =conn.cursor()
cursor.execute("update visits set num=0 where name='visitor';")
conn.commit()
conn.close()
            

@app.route("/api/v1/users",methods=['POST'])
def adduser():
	fd=open("check.txt","r")
	temp=fd.read()
	count=int(temp)
	count+=1
	fd.close()

	fd=open("check.txt","w")
	fd.write(str(count))
	fd.close()

	flag = False
	if flask.request.method=='POST':
		parser = reqparse.RequestParser()
		parser.add_argument("username")
		parser.add_argument("password")
		args = parser.parse_args()
		#print(args["username"],args["password"])
		pwd = args["password"]
		#pwdlist = list(pwd)
		flag = all(c in string.hexdigits for c in pwd)
		if len(pwd)==40 and flag==True:
			conn = mysql.connect()
			cursor =conn.cursor()
			#conn.commit()
			cursor.execute("select username from user where username='"+args["username"]+"';")
			cursor.execute("update visits set num=num+1 where name='visitor';")
			conn.commit()
			conn.close()
			if cursor.rowcount==0:
				cursor.execute("insert into user(username,password) values('"+args["username"]+"','"+args["password"]+"');")
				conn.commit()
				return "{}",201
			else:#for non unique user
				return "{}",400
		else:#for invalid password
			return "{}",400
	else:
		return "{}",405

@app.route("/api/v1/checkpassword",methods=['POST'])
def checkpassword():

    fd=open("check.txt","r")
    temp=fd.read()
    count=int(temp)
    count+=1
    fd.close()

    fd=open("check.txt","w")
    fd.write(str(count))
    fd.close()
    #flag = False
    if flask.request.method=='POST':
        parser = reqparse.RequestParser()
        parser.add_argument("username")
        parser.add_argument("password")
        args = parser.parse_args()
        #print(args["username"],args["password"])
        un = args["username"]
        pwd = args["password"]
        conn=mysql.connect()
        cursor =conn.cursor()
        cursor.execute("update visits set num=num+1 where name='visitor';")
            #conn.commit()
        cursor.execute("select username from user where username='"+args["username"]+"';")
        if cursor.rowcount==0:
            conn.close()
            return jsonify({"data":"username doesn't exist"}),432
        else:
            cursor.execute("select password from user where username='"+args["username"]+"';")
            pwd_db = cursor.fetchone()
            print(pwd_db[0])
            print(pwd)
            conn.commit()
            conn.close()
            if pwd_db[0] == pwd:
                print("it works")
                return "{}",200
            else:
                return jsonify({"data":"password and username don't match"}),453
                #return "username doesn't exist",453
    else:
        return "{}",405

@app.route("/api/v1/users/<string:userName>",methods=['DELETE'])
def removeuser(userName):

	fd=open("check.txt","r")
	temp=fd.read()
	count=int(temp)
	count+=1
	fd.close()

	fd=open("check.txt","w")
	fd.write(str(count))
	fd.close()

	if flask.request.method=='DELETE':
		conn = mysql.connect()
		cursor =conn.cursor()
		cursor.execute("update visits set num=num+1 where name='visitor';")
		conn.commit()
		cursor.execute("select username from user where username='"+userName+"';")
		if cursor.rowcount!=0:
			cursor.execute("update act set username='anonymous' where username='"+userName+"';")
			cursor.execute("delete from user where username='"+userName+"';")
			conn.commit()
			conn.close()
			return "{}",200
		else:
			return "{}",400
	else:
		return "{}",405


@app.route('/api/v1/users',methods=['GET'])
def UserList():
    fd=open("check.txt","r")
    temp=fd.read()
    count=int(temp)
    count+=1
    fd.close()

    fd=open("check.txt","w")
    fd.write(str(count))
    fd.close()

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("update visits set num=num+1 where name='visitor';")
            #conn.commit()
    #conn.commit()
    cursor.execute("select username from user")
    allusers=cursor.fetchall()
    print(allusers)
    au=[row[0] for row in allusers]
    print(au)
    conn.commit()
    conn.close()
    if(allusers):
        return jsonify(au),200
    else:
        return jsonify({}),204

@app.route('/api/v1/_count',methods=['GET'])
def count():
    fd=open("check.txt","r")
    ctr=fd.read()
    c=int(ctr)
    fd.close()
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("select num from visits where name='visitor';")
    count = cursor.fetchone();
    print("count[0]",count[0])
    print("count",count)
    conn.commit()
    conn.close()
    return jsonify(count[0]),200

@app.route('/api/v1/_count',methods=['DELETE'])
def reset():
    fd=open("check.txt","w")
    fd.write('0')
    fd.close()
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("update visits set num=0 where name='visitor';")
    #count = cursor.fetchone();
    #print("count[0]",count[0])
    #print("count",count)
    conn.commit()
    conn.close()
    return jsonify({}),200

app.run(host="0.0.0.0",port=3000,debug=True)
conn.close()
