from flask import Flask
import flask
from flask import request
from flask import jsonify
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask_restful import Api, Resource, reqparse
import json
import string
app = Flask(__name__)
CORS(app)
api = Api(app)

# users = [
#     {
#         "username": "Nicholas",
#         "password": 42
#     },
#     {
#         "username": "Elvin",
#         "password": 32
#     },
#     {
#         "username": "Jass",
#         "password": 22
#     }
# ]
# categories = [
# 	{
# 		"categoryName":"fam",
# 		"number":12
# 	},
# 	{
# 		"categoryName":"fam1",
# 		"number":13
# 	},
# 	{
# 		"categoryName":"fam2",
# 		"number":14
# 	}

# ]
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'cc'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
	
@app.route("/api/v1/users",methods=['POST'])
def addduser():
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
			cursor =conn.cursor()
			conn.commit()
			cursor.execute("select username from user where username='"+args["username"]+"';")
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

@app.route("/api/v1/users/<string:userName>",methods=['DELETE'])
def removeuser(userName):
	if flask.request.method=='DELETE':
		cursor =conn.cursor()
		conn.commit()
		cursor.execute("select username from user where username='"+userName+"';")
		if cursor.rowcount!=0:
			cursor.execute("delete from user where username='"+userName+"';")
			conn.commit()
			return "{}",200
		else:
			return "{}",400
	else:
		return "{}",405

@app.route("/api/v1/categories",methods=['GET','POST'])
def cat():
	if flask.request.method=='GET':
		cursor =conn.cursor()
		conn.commit()
		cursor.execute("SELECT categoryname,numberofacts from category")
		conn.commit()
		categories = cursor.fetchall()
		print(categories)
		if(categories):
			return jsonify(dict(categories)),200
		else:
			#return "not found",404
			return "{}",204
	elif flask.request.method=='POST':
		parser = reqparse.RequestParser()
		parser.add_argument("categoryName")
		args = parser.parse_args()
		cursor =conn.cursor()
		conn.commit()
		cursor.execute("select numberofacts from category where categoryname='"+args["categoryName"]+"';")
		if cursor.rowcount==0:
			cursor.execute("insert into category(categoryname,numberofacts) values('"+args["categoryName"]+"', 0);")
			conn.commit()
			return "{}",201
		else:
			return "{}",400
	else:
		return "{}",405

@app.route("/api/v1/categories/<string:categoryName>",methods=['DELETE'])
def delcat(categoryName):
	cursor =conn.cursor()
	conn.commit()
	cursor.execute("select numberofacts from category where categoryName='"+categoryName+"';")
	if cursor.rowcount!=0:
		cursor.execute("delete from category where categoryname='"+categoryName+"';")
		conn.commit()
		return "{}",200
	else:
		return "{}",400
	
#please add the remaining functions here, mkae sure to handle all error codes as per the spec, and enure
#that the db is correct for all queries

  
app.run(debug=True)