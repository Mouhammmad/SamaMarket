import json,sys,urllib.request,urllib.error
base='http://127.0.0.1:8000'
# 1) register (ignore if exists)
try:
    req=urllib.request.Request(base+'/api/comptes/register/', data=json.dumps({"username":"apitest","email":"apitest@example.com","password":"Testpass123","role":"CUSTOMER"}).encode('utf-8'), headers={'Content-Type':'application/json'})
    resp=urllib.request.urlopen(req)
    print('REGISTER:', resp.status, resp.read().decode())
except urllib.error.HTTPError as e:
    print('REGISTER HTTPError', e.code, e.read().decode())
except Exception as e:
    print('REGISTER error', e)
# 2) token
try:
    req=urllib.request.Request(base+'/api/token/', data=json.dumps({"username":"apitest","password":"Testpass123"}).encode('utf-8'), headers={'Content-Type':'application/json'})
    resp=urllib.request.urlopen(req)
    body=resp.read().decode()
    print('TOKEN RESPONSE:', body)
    j=json.loads(body)
    access=j.get('access')
except urllib.error.HTTPError as e:
    print('TOKEN HTTPError', e.code, e.read().decode()); sys.exit(0)
except Exception as e:
    print('TOKEN error', e); sys.exit(0)
# 3) call panier ajouter
if not access:
    print('No access token obtained')
    sys.exit(0)
try:
    payload={"produit_id":1,"quantite":2}
    req=urllib.request.Request(base+'/api/commandes/panier/ajouter/', data=json.dumps(payload).encode('utf-8'), headers={'Content-Type':'application/json','Authorization':f'Bearer {access}'})
    resp=urllib.request.urlopen(req)
    print('PANIER ADD:', resp.status, resp.read().decode())
except urllib.error.HTTPError as e:
    print('PANIER HTTPError', e.code, e.read().decode())
except Exception as e:
    print('PANIER error', e)
