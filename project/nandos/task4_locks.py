from flask import Flask
import flask
from flask import request, redirect
from flask import jsonify
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask_restful import Api, Resource, reqparse
import json
import string
import datetime
import base64
import os
import re
application = Flask(__name__)
app = application
CORS(app,support_credentials=True)
api = Api(app)
import threading
import time
import random
import subprocess
sem = threading.Semaphore()
docsem = [threading.Semaphore()]*10
ports={8000:"act8000",8001:"",8002:"",8003:"",8004:"",8005:"",8006:"",8007:"",8008:"",8009:""}
turn=-1 #turn in round robin
numreq=0
started=0
permitted_get=["api/v1/act","api/v1/category","api/v1/allacts","api/v1/categories/acts","api/v1/categories","api/v1/acts/count"]
permitted_post=["api/v1/acts","api/v1/categories","api/v1/acts/upvote"]
permitted_delete = ["api/v1/_count"]

def resetRequests():
    while(1):
        #delete container with container id = ports[p]
        #exec("docker rm "+ports[p])
        global numreq
        global turn
        global ports
        time.sleep(30)
        mustCount=int(numreq/20)+1
        numreq=0
        mustCount=min(mustCount,10)
        print("I WANT SEM\n\n\n")
        for e in docsem:
            e.acquire()
        print("SEM WITH resetRequests")
        used ={k:v for k,v in ports.items() if len(ports[k])>=4} 
        for e in docsem:
            e.release()
        print("RESET IS NOW POOR")
        currentCount=len(used.keys())
        print("NEED ",mustCount,"BUT HAVE ONLY",currentCount)
        diff=currentCount-mustCount
        while(diff>0):
            for e in docsem:
                e.acquire()
            used ={k:v for k,v in ports.items() if len(ports[k])>=4}
            print("YOU HAVE",len(used))
            p=list(used.keys())[-1] 
            
            temp=str(ports[p])
            if(len(temp)<=7):
                continue
            ports[p]=""
            for e in docsem:
                e.release()
            docsem[p-8000].acquire()
            
            #delete container with container id = ports[p]
            #exec("docker rm "+ports[p])
            print("REDUCE CONTAINER",temp)
            subprocess.run(["docker", "exec", temp, "./stop.sh"],stdout=subprocess.DEVNULL
)
            subprocess.run(["docker","stop",temp],stdout=subprocess.DEVNULL
)
            subprocess.run(["docker", "rm", temp],stdout=subprocess.DEVNULL)
            docsem[p-8000].release()
            # print("exec")
            # sem.acquire()
            # used ={k:v for k,v in ports.items() if len(ports[k])>=4}
            # sem.release()
            diff=diff-1
            
            # print("CURRENTLY",currentCount)
        while(diff<0):
            for e in docsem:
                e.acquire()
            used ={k:v for k,v in ports.items() if len(ports[k])>=4}
            
            lastused=list(used.keys())[-1]
            l=[p for p in ports.keys() if p>lastused][0]
            for e in docsem:
                e.release()
            # p=list(set(ports.keys()-used.keys()))[0]
            newc = "act"+str(l)
            # print("POOPIE\n")
            #exec("docker run -p "+str(p)+":"+str(p)+" --net=mynet --name=act"+str(p)+" imagename")
            docsem[l-8000].acquire()
            subprocess.run(["docker", "run","-d","-p",str(l)+":"+str(3000),"--network","mynet","--entrypoint=./acts.sh","--name="+newc,"nandosnv/finalact"],stdout=subprocess.DEVNULL)
            # print(" ".join(["docker", "run","-d","-p",str(p)+":"+str(3000),"--network","mynet","--entrypoint=./acts.sh","--name="+newc,"nandosnv/finalact"]))
            print("CREATED CONTAINER",newc)
            # sem.acquire()
            ports[l]=newc
            docsem[l-8000].release()
            
            diff=diff+1
        # sem.release()
        # print("RELEASED")

@app.route('/<path:text>',methods=['GET','POST','DELETE','PUT'])
def apis(text):
    #receive request with path
    #analyze path and redirect only if path is of form /act
    #maintain global variable roundrobinpointer
    global turn
    global ports
    global numreq
    global started
    numreq=numreq+1
    # print("APIS!")
    # print(text)
    if(numreq==1):
        if(started==0):
            # print("STARTED TIMER")
            t = threading.Thread(target = healthCheck)
            # print("THREAD CREATED\n\n\n\n")
            started=1
            t.start()
        #start this function in parallel      
            t2 = threading.Thread(target = resetRequests)
            t2.start()
    # print("AVAILABLE D")
    for e in docsem:
        e.acquire()
    print("ACQUIRED <Y LIFE")
    available ={k:v for k,v in ports.items() if len(ports[k])>=7} 
    # sem.release()
    count=len(available.keys())
    # print("AVAILABLE C",available)
    turn=(turn+1)%count
    
    p=list(available.keys())[turn]
    print("SERVICED BY",ports[p])
    for e in docsem:
        e.release()
    # print("RELEASED in apis\n\n\n\n\n")
    host="localhost"
    port=str(p)
    if(text!='api/v1/cleanslate'):
        # print('poop\n', 'http://'+str(host)+':'+str(p)+'/'+text)
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
                if(x!=None or y!=None):
                        return redirect('http://'+str(host)+':'+str(port)+'/'+text,code=307)
    else:
        return redirect(url_for('http://'+str(host)+':'+str(p)+'/'+text))


@app.route('/api/v1/cleanslate/',methods=['GET'])
def cleanSlate():
    global numreq
    numreq=0
    global turn
    turn=-1
    mustCount=1
    # print("CLEANSLATE NEED ONLY ",mustCount)
    for e in docsem:
        e.acquire()
    used ={k:v for k,v in ports.items() if len(ports[k])>0}
    for e in docsem:
        e.release() 
    currentCount=len(used.keys())
    while(currentCount>mustCount):
        for e in docsem:
            e.acquire()
        used ={k:v for k,v in ports.items() if len(ports[k])>0}
        for e in docsem:
            e.release()
        p=list(used.keys())[-1] 
        #delete container with container id = ports[p]
        #exec("docker rm "+ports[p])
        for e in docsem:
            e.acquire()
        temp=str(ports[p])
        ports[p]=""
        for e in docsem:
            e.release()
        print("REMOVING CONTAINER")
        docsem[p-8000].acquire()
        subprocess.run(["docker", "exec", "act"+temp, "./stop.sh"],stdout=subprocess.DEVNULL)
        subprocess.run(["docker","stop",temp],stdout=subprocess.DEVNULL)
        subprocess.run(["docker", "rm", temp],stdout=subprocess.DEVNULL)
        # print("exec")
        docsem[p-8000].release()
        for e in docsem:
            e.acquire()
        used ={k:v for k,v in ports.items() if len(ports[k])>0}
        for e in docsem:
            e.release()
        currentCount=len(used.keys())
        # print("CURRENTLY",currentCount)
    # sem.release()

def healthCheck():
    global numreq
    global ports
    while(1):
        for e in docsem:
            e.acquire()
        print("I AM THE WOPRST")
        available ={k:v for k,v in ports.items() if len(ports[k])>0}
        for e in docsem:
            e.release()
        for p in available.keys():
            v=heartbeat(p)
            if v==500:
                #delete container with container id = ports[p]
                #exec("docker rm "+ports[p])
                docsem[p-8000].acquire()
                # sem.acquire()
                temp=str(ports[p])
                ports[p]="DEAD"
                # sem.release()
                print("REPLACING CONTAINER",temp)
                subprocess.run(["docker", "exec", temp, "./stop.sh"],stdout=subprocess.DEVNULL)
                print(["docker", "exec", temp, "./stop.sh"])
                subprocess.run(["docker","stop",temp],stdout=subprocess.DEVNULL)
                print(["docker","stop",temp])
                subprocess.run(["docker","rm",temp],stdout=subprocess.DEVNULL)
                print(["docker","rm",temp])
                #newc = create new container with port = p
                #exec("docker run -p "+str(p)+":"+str(p)+" --net=mynet --name=act"+str(p)+" imagename")
                
                #set ports[p]=newc
                newc = "act"+str(p)
                #exec("docker run -p "+str(p)+":"+str(p)+" --net=mynet --name=act"+str(p)+" imagename")
                # ports[p]=newc
                subprocess.run(["docker", "run","-d", "-p",str(p)+":"+str(3000),"--network","mynet","--entrypoint=./acts.sh","--name="+newc,"nandosnv/finalact"],stdout=subprocess.DEVNULL)
                print(["docker", "run","-d", "-p",str(p)+":"+str(3000),"--network","mynet","--entrypoint=./acts.sh","--name="+newc,"nandosnv/finalact"])
                
                
                print("ADDED HEALTHY CONTAINER")
                # sem.acquire()
                ports[p]="act"+str(p)
                print("X",ports[p],end=" ")
                # sem.release()
                docsem[p-8000].release()
            else:
                print("-",ports[p],numreq,end=" ")
        print("")
        time.sleep(1)
    # keys=8000-8010
    # poll each key
    # if key has a container id
    #     if unhealthy
    #         delete cid, 
    #         create new cid
    #         set key:newcid
    #     else
    #         continue
    # else
    #     goto next port
def heartbeat(p):
    # print(".")
    # put the heartbeat API call here
    if(p==8005 or p==8001 or p==8010):
        return random.choice([500,200])
    else:
        return 200

app.run(host="0.0.0.0",port=3000,debug=True)


# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
# apis("api/v1/acts")
