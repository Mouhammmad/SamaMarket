import json
import urllib.request

url = 'http://127.0.0.1:8000/api/token/'
creds = {'username': 'vendeur_test', 'password': 'Test1234'}
data = json.dumps(creds).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode())
