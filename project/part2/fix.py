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
import numpy as np
from numpy.random import choice
import threading
import time
import random
import subprocess

application = Flask(__name__)
app = application
CORS(app,support_credentials=True)
api = Api(app)

sem = threading.Semaphore()
docsem = [threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore()]
ports={8000:"act8000",8001:"",8002:"",8003:"",8004:"",8005:"",8006:"",8007:"",8008:"",8009:""}

turn=-1 #turn in round robin
numreq=0
started=0

permitted_get=["api/v1/act","api/v1/category","api/v1/allacts","api/v1/categories/acts","api/v1/categories","api/v1/acts/count"]
permitted_post=["api/v1/acts","api/v1/categories","api/v1/acts/upvote"]
permitted_delete = ["api/v1/_count"]

def resetRequests():
    global numreq
    global turn
    global ports
    while(1):
        # 2min sleep time to check the number of requests
        time.sleep(30)
        mustCount=int(numreq/20)+1
        numreq=0
        mustCount=min(mustCount,10)

        #used has the containers that are healthy, or that are unhealthy and in process of revival
        for i in range(len(docsem)):
            docsem[i].acquire()
        used ={k:v for k,v in ports.items() if len(ports[k])>=4} 
        currentCount=len(used.keys())
        for i in range(len(docsem)):
            docsem[i].release()

        diff=currentCount-mustCount
        #start reducing containers
        while(diff>0):
            #wait for revival of unhealthy containers and then start deleting
            for k in sorted(list(ports.keys()),reverse=True):
                if ports[k]=="":
                    continue
                while(ports[k]=='DEAD'):
                    continue
                docsem[k-8000].acquire()
                print("Reset req with diff>0 Claimed by",k)
                temp = ports[k]
                print("REDUCE CONTAINER",temp)
                subprocess.run(["docker", "exec", temp, "./stop.sh"],stdout=subprocess.DEVNULL)
                print("reduce sh")    
                subprocess.run(["docker","stop",temp],stdout=subprocess.DEVNULL)
                print("reduce stop")
                subprocess.run(["docker", "rm", temp],stdout=subprocess.DEVNULL)
                print("reduce rm")
                ports[k]=""
                docsem[k-8000].release()
                print("Reset req with diff>0 Released by",k)
                diff = diff-1
                if(diff==0):
                    break

        #start adding containers
        while(diff<0):
            for k in sorted(list(ports.keys())):
                if ports[k]!="":
                    continue
                docsem[k-8000].acquire()
                # print("Reset req with diff<0 Claimed by",k)
                temp = "act"+str(k)
                print("ADD CONTAINER",temp)
                subprocess.run(["docker", "run","-d","-p",str(k)+":"+str(3000),"--network","mynet","--entrypoint=./acts.sh","--name="+temp,"nandosnv/finalact"],stdout=subprocess.DEVNULL)
                ports[k]=temp
                docsem[k-8000].release()
                # print("Reset req with diff<0 Released by",k)
                diff = diff+1
                if(diff==0):
                    break

def healthCheck():
    global numreq
    global ports
    while(1):
        for k in list(ports.keys()):
            obtained = docsem[k-8000].acquire(blocking=False)
            if obtained==False:
                continue
            print("healthCheck Claimed ",k)
            if len(ports[k]) >= 7:
                value = heartBeat(k)
                if value == 500:
                    temp = ports[k]
                    ports[k]="DEAD"

                    #now delete container with id 'k'
                    # print("REPLACING CONTAINER",temp)
                    subprocess.run(["docker", "exec", temp, "./stop.sh"],stdout=subprocess.DEVNULL)
                    print("replace sh")
                    subprocess.run(["docker","stop",temp],stdout=subprocess.DEVNULL)
                    print("replace stop")
                    subprocess.run(["docker","rm",temp],stdout=subprocess.DEVNULL)
                    print("replace rm")
                    
                    #create a new container with the old name and port
                    subprocess.run(["docker", "run","-d", "-p",str(k)+":"+str(3000),"--network","mynet","--entrypoint=./acts.sh","--name="+temp,"nandosnv/finalact"],stdout=subprocess.DEVNULL)
                    ports[k] = temp
                    print("X",ports[k],end=" ")
                else:
                    print("-",ports[k],numreq,end=" ")
                # print("")
            docsem[k-8000].release()
            print("healthCheck Released ",k)
        print("")
        time.sleep(1)

def heartBeat(p):
    if(p==8005 or p==8001 or p==8010):
        return choice([500,200],p=[0.2,0.8])
    else:
        return 200

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
    
    if(numreq==1):
        if(started==0):
            t = threading.Thread(target = healthCheck)
            started=1
            t.start()
            #start this function in parallel      
            t2 = threading.Thread(target = resetRequests)
            t2.start()

    #round-robin
    # for i in range(len(docsem)):
    #     docsem[i].acquire()
    # docsem[0].acquire()
    # docsem[1].acquire()
    #print("yay")
    # available ={k:v for k,v in ports.items() if len(ports[k])>=7} 
    # count=len(available.keys())
    count=len(list(ports.keys()))
    turn=(turn+1)%count
    while(len(ports[turn+8000])<7):
        turn=(turn+1)%count
    p=turn+8000    
    # docsem[0].release()
    # docsem[1].release()
    # for i in range(len(docsem)):
        # docsem[i].release()    


    #which container's turn it is now
    # p=list(available.keys())[turn]
    print("SERVICED BY",ports[p])

    #redirect the API request to the container found above
    host="localhost"
    port=str(p)
    if(text!='api/v1/cleanslate'):
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


app.run(host="0.0.0.0",port=3000,debug=True)