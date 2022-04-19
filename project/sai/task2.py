# from flask import Flask
# import flask
# from flask import request
# from flask import jsonify
# from flask_cors import CORS, cross_origin
# from flaskext.mysql import MySQL
# from flask_restful import Api, Resource, reqparse
# import json
# import string
# import datetime
# import base64
# import os
# application = Flask(__name__)
# app = application
# CORS(app,support_credentials=True)
# api = Api(app)
import threading
import time
import random
import subprocess
sem = threading.Semaphore()
ports={8000:"nandos",8001:"",8002:"",8003:"",8004:"",8005:"",8006:"",8007:"",8008:"",8009:""}
turn=0 #turn in round robin
numreq=0

def resetRequests():
    while(1):
        #delete container with container id = ports[p]
        #exec("docker rm "+ports[p])
        global numreq
        global turn
        global ports
        time.sleep(5)
        mustCount=int(numreq/20)+1
        numreq=0
        mustCount=min(mustCount,10)
        print("NEED ONLY ",mustCount)
        sem.acquire()
        used ={k:v for k,v in ports.items() if len(ports[k])>0} 
        currentCount=len(used.keys())
        while(currentCount>mustCount):
            used ={k:v for k,v in ports.items() if len(ports[k])>0}
            p=list(used.keys())[0] 
            #delete container with container id = ports[p]
            #exec("docker rm "+ports[p])
            ports[p]=""
            print("REMOVING CONTAINER")
            subprocess.run(["sleep","5"])
            subprocess.run(["echo", "hi"])

            print("exec")
            used ={k:v for k,v in ports.items() if len(ports[k])>0}
            currentCount=len(used.keys())
            print("CURRENTLY",currentCount)
        while(currentCount<mustCount):
            used ={k:v for k,v in ports.items() if len(ports[k])>0}
            p=list(set(ports.keys()-used.keys()))[0]
            #newc = create new container with port = p
            # subprocess.run(list("docker run -d -p "+str(p)+":"+str(p)+" --net=mynet --name=act"+str(p)+"  --entrypoint='./acts.sh' w_act".split(" ")))
            l2=str("docker run -d -p "+str(p)+":3000"+" --net=mynet --name=act"+str(p)+" --entrypoint=./acts.sh w_act").split(" ")
            testys=str("docker run -d -p "+str(p)+":3000"+" --net=mynet --name=act"+str(p)+" --entrypoint=./acts.sh w_act")
            
            print(testys)
            print(l2)
            subprocess.run(testys.split(" "))
            ports[p]="act"+str(p)
            used ={k:v for k,v in ports.items() if len(ports[k])>0}
            #set ports[p]=newc
            print("ADDING NEW CONTAINER")
            currentCount=len(used.keys())
        sem.release()

# @app.route("/api/v1/",methods=['GET','POST','DELETE','PUT'])
def apis(path):
    #receive request with path
    #analyze path and redirect only if path is of form /act
    #maintain global variable roundrobinpointer
    global turn
    global ports
    global numreq
    numreq=numreq+1
    if(numreq==1):
        print("STARTED TIMER")
        #start this function in parallel      
        t2 = threading.Thread(target = resetRequests)
        t2.start()
    sem.acquire()
    available ={k:v for k,v in ports.items() if len(ports[k])>0} 
    count=len(available.keys())
    print("AVAILABLE C",available)
    
    p=list(available.keys())[turn]
    print(ports[p])
    turn=(turn+1)%count
    #redirect to port p
    sem.release()

def healthCheck():
    while(1):
        available ={k:v for k,v in ports.items() if len(ports[k])>0}
        for p in available.keys():
            v=heartbeat(p)
            if v==500:
                #delete container with container id = ports[p]
                #exec("docker rm "+ports[p])
                ports[p]=""
                #newc = create new container with port = p
                #exec("docker run -p "+str(p)+":"+str(p)+" --net=mynet --name=act"+str(p)+" imagename")
                
                #set ports[p]=newc
                ports[p]="act"+str(p)
                print("X",ports[p],end=" ")
            else:
                print("-",ports[p],end=" ")
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
    if(p==8002 or p==8004 or p==8006):
        return random.choice([500,200])
    else:
        return 200

# healthCheck()

t = threading.Thread(target = healthCheck)
t.start()
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
apis("api/v1/acts")
