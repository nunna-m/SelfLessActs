from flask import Flask,jsonify,abort,request
from flask_restful import Api, Resource, reqparse
from flaskext.mysql import MySQL
import json
import datetime
import base64
import flask
app = Flask(__name__)
api = Api(app)

mysql = MySQL(app)
app.config['MYSQL_DATABASE_USER'] = 'newuser'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'CC'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
conn = mysql.connect()
cursor =conn.cursor()

names = ('actId','username','timestamp','caption','upvotes','imgB64')

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
            return "not found",404
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
    return "Category not found",405

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
        p[names[2]]=acts[i][2].strftime('%d-%m-%Y:%S:%M:%H')
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
    p = request.json;
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
        return "act not found",400
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

#upload act : (Yet to be finished)
@app.route("/api/v1/acts",methods=['POST'])
def uploadact():
    a = request.json
    cursor.execute('Select * from act Where actid=%s;',a['actId'])
    if cursor.fetchone() != None:
        return jsonify({"act aldready present":"400"}),400
    d = datetime.datetime.strptime(str(a['timestamp']),'%d-%m-%Y:%S:%M:%H')
    try:
        cursor.execute('Select * from user Where username=%s;',a['username'])
        if cursor.fetchone() == None:
            return jsonify({"user not present":"400"}),400
        img = base64.decodestring(a['imgB64'].encode())
    except:
        return jsonify({}),400
    
    try:
        if(a['categoryName']!=None):
            x=6
    except:
        return jsonify({}),400

    try:
        if(a['upvote']!=None):
            return jsonify({}),400
    except:
        x=5
    cursor.execute('INSERT INTO act values (%s,%s,%s,%s,%s,%s,%s)',(a['actId'],a['username'],str(d),a['caption'],'0',str('/img'+str(a['actId'])+'.png'),a['categoryName']))
    conn.commit()
    try:
        cursor.execute('Update category SET numberofacts = numberofacts+1 Where categoryname=%s;',a['categoryName'])
        conn.commit()
    except:
        cursor.execute('INSERT INTO category Values (%s,%s);',(a['categoryName'],'1'))
        conn.commit()
    write_img = open('img'+str(a['actId'])+'.png','wb')
    write_img.write(img)
    write_img.close()
    return jsonify({}),201


app.run(debug=True)