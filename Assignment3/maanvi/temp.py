import json, requests
payload = {}
r = requests.get('http://192.168.1.6:3036/api/v1/categories',data=json.dumps(payload))
#print(type(r.json))
#print(type(r.text))
print(r.json()["cats"])