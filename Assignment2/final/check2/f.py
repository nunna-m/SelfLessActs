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
CORS(app,support_credentials=True)
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
		args = request.json;
		print(args)
		cursor =conn.cursor()
		conn.commit()
		cursor.execute("select numberofacts from category where categoryname='"+args[0]+"';")
		if cursor.rowcount==0:
			cursor.execute("insert into category(categoryname,numberofacts) values('"+args[0]+"', 0);")
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

@app.route('/api/v1/categories/<categoryName>/acts/size',methods=['GET'])
def ActNum(categoryName):
    cursor.execute('select numberofacts from category where categoryname=%s',categoryName)
    x=cursor.fetchone()

    if(x):
        return jsonify(x),200
    return jsonify({}),204	

@app.route("/api/v1/allacts",methods=['GET'])
def  allacts():
    cursor.execute('Select * from act Order by posttime desc;')
    acts = cursor.fetchall()
    l = []
    i = 0 
    k = len(acts)
    while i<k and i<100:
        p = dict()
        p[names[0]]=acts[i][0]
        p[names[1]]=acts[i][1]
        p[names[2]]=acts[i][2].strftime('%d-%m-%Y:%S-%M-%H')
        p[names[3]]=acts[i][3]
        p[names[4]]=acts[i][4]
        img = open(acts[i][5][1:],'rb')
        p[names[5]] = str(base64.encodestring(img.read()),'utf-8')[:-1]
        img.close()
        l.append(p)
        i = i+1
    return jsonify(l),200

#list acts in a range
@app.route("/api/v1/categories/<categoryName>/acts",methods=['GET'])
def rangeacts(categoryName):
    cursor.execute('Select * from category Where categoryname=%s;',categoryName)
    cat = cursor.fetchone()
    try:
        start = int(request.args['start'])
        end = int(request.args['end'])
    except:
        start=1
        end = cat[1]
    if(cat==None):
        return jsonify({}),400
    if(start<1 or end>int(cat[1])):
        return jsonify({"wrong params":"1"}),400
    if(end<start):
        return jsonify({}),204

    if((end-start+1)>100):
        return jsonify({}),413
    cursor.execute('Select * from act Where category = %s Order by posttime desc;',categoryName)
    acts = cursor.fetchall()
    l = []
    for i in range(start-1,end):
        p = dict()
        p[names[0]]=acts[i][0]
        p[names[1]]=acts[i][1]
        p[names[2]]=acts[i][2].strftime('%d-%m-%Y:%S-%M-%H')
        p[names[3]]=acts[i][3]
        p[names[4]]=acts[i][4]
        img = open(acts[i][5][1:],'rb')
        p[names[5]] = str(base64.encodestring(img.read()),'utf-8')[:-1]
        img.close()
        l.append(p)
    return jsonify(l),200

#upvotes 
@app.route("/api/v1/acts/upvote",methods=['POST'])
def upvote():
    p = request.get_json()
    print(p)
    if not p:
        return jsonify({}),400
    cursor.execute('Select * from act Where actid=%s;',p)
    if cursor.fetchone() == None:
        return jsonify({}),400
    
    try:
        cursor.execute('Update act SET upvotes = upvotes+1 Where actid=%s;',p)
        conn.commit()
        return jsonify({}),200
    except:
        return jsonify({}),400

#Remove act
@app.route("/api/v1/acts/<actid>",methods=['DELETE'])
def removeact(actid):
    cursor.execute('Select * from act Where actid=%s;',actid)
    if cursor.fetchone() == None:
        return jsonify({}),400
    try:
        cursor.execute('SELECT category from act Where actid=%s;',actid)
        p=cursor.fetchone()
        cursor.execute('DELETE from act Where actid=%s;',actid)
        conn.commit()

        cursor.execute('update category set numberofacts = numberofacts-1 where categoryname = %s;',p[0])
        conn.commit()
        return jsonify({}),200
    except Error as error:
        raise error

#upload act : 
@app.route("/api/v1/acts",methods=['POST'])
def uploadact():
    parser = reqparse.RequestParser()
    parser.add_argument('actId')
    parser.add_argument('username')
    parser.add_argument('timestamp')
    parser.add_argument('caption')
    parser.add_argument('imgB64')
    parser.add_argument('categoryName')
    a = parser.parse_args()
    print(a)
    cursor.execute('Select * from act Where actid=%s;',a['actId'])
    if cursor.fetchone() != None:
        return jsonify({}),400
   
    try:
        d = datetime.datetime.strptime(str(a['timestamp']),'%d-%m-%Y:%S-%M-%H')
        cursor.execute('Select * from user Where username=%s;',a['username'])
        if cursor.fetchone() == None:
            return jsonify({}),400
        img = base64.decodestring(a['imgB64'].encode())
    except:
        return jsonify({}),400
    
    cursor.execute("select numberofacts from category where categoryName='"+a['categoryName']+"';")
    if cursor.rowcount!=0:
        cursor.execute('Update category SET numberofacts = numberofacts+1 Where categoryname=%s;',a['categoryName'])
        conn.commit()
    else:
        return jsonify({}),400
    
    try:
        if(a['categoryName']!=None):
            x=6
    except:
        return jsonify({}),400

    try:
        if(a['upvotes']!=None):
            return jsonify({}),400
    except:
        x=5
    cursor.execute('INSERT INTO act values (%s,%s,%s,%s,%s,%s,%s)',(a['actId'],a['username'],str(d),a['caption'],'0',str('/img'+str(a['actId'])+'.png'),a['categoryName']))
    conn.commit()
    
    write_img = open('img'+str(a['actId'])+'.png','wb')
    write_img.write(img)
    write_img.close()
    return jsonify({}),201

#please add the remaining functions here, mkae sure to handle all error codes as per the spec, and enure
#that the db is correct for all queries

  
app.run(debug=True)