import urllib.request, json
url = 'http://127.0.0.1:8000/api/token/refresh/'
refresh = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc4NjE5MzQyOSwiaWF0IjoxNzg2MTA3MDI5LCJqdGkiOiI5MjNkM2FlMTAzZjk0MzdlYmYwNmExMWUxOTFkOTBmNyIsInVzZXJfaWQiOiIxNSJ9.JuGaomrD1GZ1hF43wYjyUQI-Tim4ASmbvZveBKq20NQ'
data = json.dumps({'refresh': refresh}).encode()
req = urllib.request.Request(url, data=data, headers={'Content-Type':'application/json'})
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode())
