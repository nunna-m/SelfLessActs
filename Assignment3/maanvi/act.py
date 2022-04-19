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

@app.route("/api/v1/categories/acts",methods=['GET'])
def userposts():
    conn = mysql.connect()
    cursor=conn.cursor()
    parser = reqparse.RequestParser()
    parser.add_argument("username")
    args = parser.parse_args()
    uns = args["username"]
    #cursor.execute('Select * from act Order by posttime desc;')
    cursor.execute("select * from act where username='"+uns+"'order by posttime desc;")
    #"insert into user(username,password) values('"+args["username"]+"','"+args["password"]+"');"
    acts = cursor.fetchall()
    conn.close()
    l = []
    i = 0 
    k = len(acts)
    while i<k and i<100:
        p = dict()
        p[names2[0]]=acts[i][0]
        p[names2[1]]=acts[i][1]
        p[names2[2]]=acts[i][2].strftime('%d-%m-%Y:%S-%M-%H')
        p[names2[3]]=acts[i][3]
        p[names2[4]]=acts[i][4]
        img = open(acts[i][5][1:],'rb')
        p[names[5]] = str(base64.encodestring(img.read()),'utf-8')[:-1]
        img.close()
        p[names2[6]]=acts[i][6]
        l.append(p)
        i = i+1
    return jsonify(l),200

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
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute('Select * from act Where actid=%s;',a['actId'])
    if cursor.fetchone() != None:
        return jsonify({}),400
   
    try:
        d = datetime.datetime.strptime(str(a['timestamp']),'%d-%m-%Y:%S-%M-%H')
        #cursor.execute('Select * from user Where username=%s;',a['username'])
        payload = {}
        r = requests.get('http://localhost:3036//api/v1/users',data=json.dumps(payload))
		#print(r.json)
		#print(r.text)
		if(r.json==None):

        #if cursor.fetchone() == None:
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
    conn.close()
    
    write_img = open('img'+str(a['actId'])+'.png','wb')
    write_img.write(img)
    write_img.close()
    return jsonify({}),201

#please add the remaining functions here, mkae sure to handle all error codes as per the spec, and enure
#that the db is correct for all queries

app.run(host="0.0.0.0",port=3036,debug=True)
conn.close()