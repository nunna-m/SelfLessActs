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

@app.route("/api/v1/categories/acts",methods=['GET'])
def userposts():

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

@app.route("/api/v1/categories",methods=['GET','POST'])
def cat():
    fd=open("check.txt","r")
    temp=fd.read()
    count=int(temp)
    count+=1
    fd.close()

    fd=open("check.txt","w")
    fd.write(str(count))
    fd.close()

    if flask.request.method=='GET':
        conn = mysql.connect()
        cursor =conn.cursor()
        #conn.commit()
        cursor.execute("SELECT categoryname,numberofacts from category")
        conn.close()
        #conn.commit()
        categories = cursor.fetchall()
        print(categories)
        if(categories):
            return jsonify(dict(categories)),200
        else:
            #return "not found",404
            return "{}",204
    elif flask.request.method=='POST':
        args=request.get_json()
        print(args)
        conn = mysql.connect()
        cursor =conn.cursor()
        #conn.commit()
        cursor.execute('select numberofacts from category where categoryname=%s;',args)
        if cursor.rowcount==0:
            cursor.execute('insert into category(categoryname,numberofacts) values(%s,0);',args)
            conn.commit()
            conn.close()
            return "{}",201
        else:
            return "{}",400
    else:
        return "{}",405

@app.route("/api/v1/categories/<string:categoryName>",methods=['DELETE'])
def delcat(categoryName):
    fd=open("check.txt","r")
    temp=fd.read()
    count=int(temp)
    count+=1
    fd.close()

    fd=open("check.txt","w")
    fd.write(str(count))
    fd.close()

    cursor.execute("select numberofacts from category where categoryName='"+categoryName+"';")
    if cursor.rowcount!=0:
        cursor.execute("delete from category where categoryname='"+categoryName+"';")
        conn.commit()
        conn.close()
        return "{}",200
    else:
        return "{}",400

@app.route('/api/v1/categories/<categoryName>/acts/size',methods=['GET'])
def ActNum(categoryName):
    fd=open("check.txt","r")
    temp=fd.read()
    count=int(temp)
    count+=1
    fd.close()

    fd=open("check.txt","w")
    fd.write(str(count))
    fd.close()

    conn = mysql.connect()
    cursor.execute('select numberofacts from category where categoryname=%s',categoryName)
    x=cursor.fetchone()
    conn.close()
    if(x):
        return jsonify(x),200
    return jsonify({}),204

@app.route("/api/v1/allacts",methods=['GET'])
def  allacts():
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
    cursor.execute('Select * from act Order by posttime desc;')
    acts = cursor.fetchall()
    #print(acts)
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
        p[names2[5]] = str(base64.encodestring(img.read()),'utf-8')[:-1]
        #print(acts[i][6])
        img.close()
        #print(p)
        p[names2[6]] = str(acts[i][6])
        #print(p[names2[6]])
        l.append(p)
        i = i+1
    return jsonify(l),200

#list acts in a range
@app.route("/api/v1/categories/<categoryName>/acts",methods=['GET'])
def rangeacts(categoryName):
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
    conn.close()
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
        conn.close()
        return jsonify({}),200
    except:
        return jsonify({}),400

#Remove act
@app.route("/api/v1/acts/<actid>",methods=['DELETE'])
def removeact(actid):
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
    cursor.execute('Select * from act Where actid=%s;',actid)
    if cursor.fetchone() == None:
        return jsonify({}),400
    try:
        cursor.execute('SELECT category from act Where actid=%s;',actid)
        p=cursor.fetchone()
        cursor.execute('DELETE from act Where actid=%s;',actid)
        conn.commit()
        os.remove('img'+actid+'.png')
        #suspect
        cursor.execute('update category set numberofacts = numberofacts-1 where categoryname = %s;',p[0])
        conn.commit()
        conn.close()
        return jsonify({}),200
    except Error as error:
        raise error

#upload act :
@app.route("/api/v1/acts",methods=['POST'])
def uploadact():
    fd=open("check.txt","r")
    temp=fd.read()
    count=int(temp)
    count+=1
    fd.close()

    fd=open("check.txt","w")
    fd.write(str(count))
    fd.close()

    parser = reqparse.RequestParser()
    parser.add_argument('actId')
    parser.add_argument('username')
    parser.add_argument('timestamp')
    parser.add_argument('caption')
    parser.add_argument('imgB64')
    parser.add_argument('categoryName')
    a = parser.parse_args()
    #print(a)
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute('Select * from act Where actid=%s;',a['actId'])
    if cursor.fetchone() != None:
        return jsonify({}),400

    try:
        d = datetime.datetime.strptime(str(a['timestamp']),'%d-%m-%Y:%S-%M-%H')
        #cursor.execute('Select * from user Where username=%s;',a['username'])
        payload = {}
        c=str(a['username'])
        print(c)
        r = requests.get('http://172.18.0.3:3000/api/v1/users',data=json.dumps(payload))
        print(r)
        userfound=0
        for i in list(r.json()):
            print(i)
            if(c==i):
              userfound=1
        if(userfound==0):
            return jsonify({}),400
        img = base64.decodestring(a['imgB64'].encode())
    except:
        print("Failed try block")
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
@app.route('/api/v1/_count',methods=['GET'])
def count():
    fd=open("check.txt","r")
    ctr=fd.read()
    c=int(ctr)
    fd.close()
    return jsonify(c),200

@app.route('/api/v1/_count',methods=['DELETE'])
def reset():
    fd=open("check.txt","w")
    fd.write('0')
    fd.close()
    return jsonify({}),200

@app.route('/api/v1/acts/count',methods=['GET'])
def NumOfActs():
    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute('Select * from act ;')
    acts = cursor.fetchall()
    num=len(acts)
    return jsonify(num),200




app.run(host="0.0.0.0",port=3000,debug=True)
conn.close()
