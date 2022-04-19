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
CORS(app,support_credentials=True,resources={r"/*":{"origins":"http://18.210.123.131"}})
api = Api(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'cc'
app.config['MYSQL_DATABASE_HOST'] = 'mysql'
mysql.init_app(app)

names = ('actId','username','timestamp','caption','upvotes','imgB64')
names2 = ('actId','username','timestamp','caption','upvotes','imgB64','category')




@app.route("/api/v1/cleanslate7019865870",methods=['GET'])
def userposts():
    conn = mysql.connect()
    cursor=conn.cursor()
    #cursor.execute('Select * from act Order by posttime desc;')
    cursor.execute("delete from act;")
    cursor.execute("delete from category;")
    conn.commit()
    conn.close()
    return jsonify("CLEARED EVERYTHING"),200

@app.route("/api/v1/categories",methods=['GET','POST'])
def cat():

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

    if flask.request.method=='GET':
        conn = mysql.connect()
        cursor =conn.cursor()
        #conn.commit()
        cursor.execute("update visits set num=num+1 where name='visitor';")
        conn.commit()
        cursor.execute("SELECT categoryname,numberofacts from category")
        # cursor.execute("update visits set num=num+1 where name='visitor';")
        conn.commit()
        #conn.close()
        #conn.commit()
        categories = cursor.fetchall()
        print(categories)
        conn.close()
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
        cursor.execute("update visits set num=num+1 where name='visitor';")
        conn.commit()
        cursor.execute('select numberofacts from category where categoryname=%s;',args)
       # cursor.execute("update visits set num=num+1 where name='visitor';")
        conn.commit()
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

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

    conn = mysql.connect()
    cursor =conn.cursor()
    cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
    cursor.execute("select numberofacts from category where categoryName='"+categoryName+"';")
    #cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
    if cursor.rowcount!=0:
        cursor.execute("delete from category where categoryname='"+categoryName+"';")
        conn.commit()
        conn.close()
        return "{}",200
    else:
        return "{}",400

@app.route('/api/v1/categories/<categoryName>/acts/size',methods=['GET'])
def ActNum(categoryName):

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

    conn = mysql.connect()
    cursor =conn.cursor()
    cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
    cursor.execute('select numberofacts from category where categoryname=%s',categoryName)
   # cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
    x=cursor.fetchone()
    conn.close()
    if(x):
        return jsonify(x),200
    return jsonify({}),204

@app.route("/api/v1/allacts",methods=['GET'])
def  allacts():

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
    cursor.execute('Select * from act Order by posttime desc;')
    acts = cursor.fetchall()
    #cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
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
        p[names2[5]] = acts[i][5]
        p[names2[6]] = str(acts[i][6])
        #print(p[names2[6]])
        l.append(p)
        i = i+1
    return jsonify(l),200

#list acts in a range
@app.route("/api/v1/categories/<categoryName>/acts",methods=['GET'])
def rangeacts(categoryName):

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
    cursor.execute('Select * from category Where categoryname=%s;',categoryName)
    #cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
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
        p[names[5]] =acts[i][5]
        l.append(p)
    return jsonify(l),200

#upvotes
@app.route("/api/v1/acts/upvote",methods=['POST'])
def upvote():

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
    p = request.get_json()
    print(p)
    if not p:
        return jsonify({}),400
    cursor.execute('Select actid from act Where actid=%s;',p)

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

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
    cursor.execute('Select actid from act Where actid=%s;',actid)
    if cursor.fetchone() == None:
        return jsonify({}),400
    try:
        cursor.execute('SELECT category from act Where actid=%s;',actid)
        p=cursor.fetchone()
        cursor.execute('DELETE from act Where actid=%s;',actid)
        conn.commit()
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

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

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
    cursor.execute("update visits set num=num+1 where name='visitor';")
    conn.commit()
    cursor.execute('Select actid from act Where actid=%s;',a['actId'])
    if cursor.fetchone() != None:
        return jsonify({}),400

    try:
        d = datetime.datetime.strptime(str(a['timestamp']),'%d-%m-%Y:%S-%M-%H')
        #cursor.execute('Select * from user Where username=%s;',a['username'])
        payload = {}
        c=str(a['username'])
        print(c)
        #r = requests.get('http://172.18.0.3:3000/api/v1/users',data=json.dumps(payload))
        r = requests.get('http://34.236.27.23:80/api/v1/users',data=json.dumps(payload),allow_redirects=False)
        
        print(r)
        userfound=0
        for i in list(r.json()):
            print(i)
            if(c==i):
              userfound=1
        #userfound=1
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
    cursor.execute('INSERT INTO act(username,posttime,caption,upvotes,image,category) values (%s,%s,%s,%s,%s,%s)',(a['username'],str(d),a['caption'],'0',a['imgB64'],a['categoryName']))
    conn.commit()
    conn.close()
    
    return jsonify({}),201

#please add the remaining functions here, mkae sure to handle all error codes as per the spec, and enure
#that the db is correct for all queries
@app.route('/api/v1/_count',methods=['GET'])
def count():

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("select num from visits where name='visitor';")
    count = cursor.fetchone()
    print("count[0]",count[0])
    print("count",count)
    conn.commit()
    conn.close()
    return jsonify([count[0]]),200

@app.route('/api/v1/_count',methods=['DELETE'])
def reset():

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute("update visits set num=0 where name='visitor';")

    conn.commit()
    conn.close()
    return jsonify({}),200

@app.route('/api/v1/acts/count',methods=['GET'])
def NumOfActs():

    file1 = open('crash.txt','r')
    value = file1.read()
    if(value=='1'):
        return jsonify({}),500
    file1.close()

    conn = mysql.connect()
    cursor=conn.cursor()
    cursor.execute('Select actid from act ;')
    acts = cursor.fetchall()
    num=len(acts)
    return jsonify([num]),200

@app.route('/api/v1/_health',methods=['GET'])
def health_check():
   
    file1 = open('crash.txt','r')
    value = file1.read()
    file1.close()
    if(value=='1'):
        return jsonify({}),500

    try:
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('Select numberofacts from category where categoryname="qwerty";')
        acts=cursor.fetchone()
        conn.commit()
        conn.close()
        return jsonify({}),200
    except  :
        return jsonify({}),500

@app.route('/api/v1/_crash',methods=['POST'])
def crash_server():
    
    file1 = open('crash.txt','r')
    val = file1.read()
    file1.close()

    if(val=='1'):#crashed
        return jsonify({}),500
    else:
        file2 = open('crash.txt','w')
        file2.write('1')
        file2.close()
        return jsonify({}),200

app.run(host="0.0.0.0",port=3000,debug=True)
conn.close()
