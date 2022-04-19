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
import requests
application = Flask(__name__)
app = application
CORS(app,support_credentials=True)
api = Api(app)

#sem = threading.Semaphore()
#docsem = [threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore(),threading.Semaphore()]

#parameters
with open('config_info.json') as json_file:  
    data = json.load(json_file)
    #print(type(data))
    initial_port = int(data['initial_port'])
    num_containers = int(data['num_containers'])
    beat = int(data['heartbeat'])
    scale_time = int(data['scale_time'])
    image_name = str(data['image_name'])
    threshold = int(data['threshold'])
    internal_port = str(data['internal_port'])

    
ports=dict()
keys = [initial_port+i for i in range(num_containers)]
ports[initial_port]="act"+str(initial_port)
for i in keys[1:]:
    ports[i]=""

#semaphore init
sem = threading.Semaphore()
docsem=[]
for val in range(num_containers):
    docsem.append(threading.Semaphore())


#ports={8000:"act8000",8001:"",8002:"",8003:"",8004:"",8005:"",8006:"",8007:"",8008:"",8009:""}

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
    global scale_time
    global threshold
    global num_containers
    global initial_port
    global image_name
    global internal_port
    while(1):
        # 2min sleep time to check the number of requests
        #time.sleep(120)
        time.sleep(scale_time)
        mustCount=int(numreq/threshold)+1
        sem.acquire()
        numreq=0
        sem.release()
        mustCount=min(mustCount,num_containers)

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
                docsem[k-initial_port].acquire()
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
                docsem[k-initial_port].release()
                print("Reset req with diff>0 Released by",k)
                diff = diff-1
                if(diff==0):
                    break

        #start adding containers
        while(diff<0):
            for k in sorted(list(ports.keys())):
                if ports[k]!="":
                    continue
                docsem[k-initial_port].acquire()
                # print("Reset req with diff<0 Claimed by",k)
                temp = "act"+str(k)
                print("ADD CONTAINER",temp)
                subprocess.run(["docker", "run","-d","-p",str(k)+":"+internal_port,"--network","mynet","--entrypoint=./acts.sh","--name="+temp,image_name],stdout=subprocess.DEVNULL)
                ports[k]=temp
                docsem[k-initial_port].release()
                # print("Reset req with diff<0 Released by",k)
                diff = diff+1
                if(diff==0):
                    break

def healthCheck():
    global numreq
    global ports
    global initial_port
    global image_name
    global beat
    global internal_port
    while(1):
        for k in list(ports.keys()):
            obtained = docsem[k-initial_port].acquire(blocking=False)
            if obtained==False:
                continue
            #print("healthCheck Claimed ",k)
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
                    subprocess.run(["docker", "run","-d", "-p",str(k)+":"+internal_port,"--network","mynet","--entrypoint=./acts.sh","--name="+temp,image_name],stdout=subprocess.DEVNULL)
                    ports[k] = temp
                    print("X",ports[k],end=" ")
                else:
                    print("-",ports[k],numreq,end=" ")
                # print("")
            docsem[k-initial_port].release()
            #print("healthCheck Released ",k)
        print("")
        time.sleep(beat)

def heartBeat(p):
    try:
        req = requests.get('http://localhost:'+str(p)+'/api/v1/_health',verify=False)
        print(req.status_code)
        return int(req.status_code)
    except:
        return 500

@app.route('/<path:text>',methods=['GET','POST','DELETE','PUT'])
def apis(text):
    #receive request with path
    #analyze path and redirect only if path is of form /act
    #maintain global variable roundrobinpointer
    global turn
    global ports
    global numreq
    global started

    #numreq=numreq+1
    
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
    while(len(ports[turn+initial_port])<7):
        turn=(turn+1)%count
    p=turn+initial_port    
    # docsem[0].release()
    # docsem[1].release()
    # for i in range(len(docsem)):
        # docsem[i].release()    


    #which container's turn it is now
    # p=list(available.keys())[turn]
    print("SERVICED BY",ports[p])

    #redirect the API request to the container found above
    host='127.0.0.1'
    port=str(p)
    if(text!='api/v1/cleanslate'):
        if flask.request.method=='GET':
                x = re.match("^api[/]v1[/]categories[/].*[/]acts$", text)
                y = re.match("^api[/]v1[/]categories[/].*[/]acts[/]size$", text)
                if(x!=None or y!=None or text in permitted_get):
                        sem.acquire()
                        numreq=numreq+1
                        sem.release()
                        if(numreq==1):
                            if(started==0):
                                t = threading.Thread(target = healthCheck)
                                started=1
                                t.start()
                                #start this function in parallel      
                                t2 = threading.Thread(target = resetRequests)
                                t2.start()
                        resp = requests.get(url=str('http://'+str(host)+':'+str(port)+'/'+text))
                        if(len(resp.content)==0):
                            return '',resp.status_code
                        return jsonify(resp.json()),resp.status_code
                        #return redirect('http://'+str(host)+':'+str(port)+'/'+text,code=302)
        if flask.request.method=='POST':
                if(text in permitted_post):
                        sem.acquire()
                        numreq=numreq+1
                        sem.release()
                        if(numreq==1):
                            if(started==0):
                                t = threading.Thread(target = healthCheck)
                                started=1
                                t.start()
                                #start this function in parallel      
                                t2 = threading.Thread(target = resetRequests)
                                t2.start()
                        resp = requests.post(url=str('http://'+str(host)+':'+str(port)+'/'+text),json=request.get_json())
                        if(len(resp.content)==0):
                            return '',resp.status_code
                        return jsonify(resp.json()),resp.status_code
                        #return redirect('http://'+str(host)+':'+str(port)+'/'+text,code=307)
        if flask.request.method=='DELETE':
                x = re.match("^api[/]v1[/]categories[/].*$",text)
                y = re.match("^api[/]v1[/]acts[/].*$",text)
                if(x!=None or y!=None):
                        sem.acquire()
                        numreq=numreq+1
                        sem.release()
                        if(numreq==1):
                            if(started==0):
                                t = threading.Thread(target = healthCheck)
                                started=1
                                t.start()
                                #start this function in parallel      
                                t2 = threading.Thread(target = resetRequests)
                                t2.start()
                        resp = requests.delete(url=str('http://'+str(host)+':'+str(port)+'/'+text),json=request.get_json())
                        if(len(resp.content)==0):
                            return '',resp.status_code
                        return jsonify(resp.json()),resp.status_code
                        #return redirect('http://'+str(host)+':'+str(port)+'/'+text,code=307)
    else:
        print("yay")
        #return redirect(url_for('http://'+str(host)+':'+str(p)+'/'+text))


# app.run(host="0.0.0.0",port=3000,debug=True)
app.run(host="0.0.0.0",port=80,debug=True)
