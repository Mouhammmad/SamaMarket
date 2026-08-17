import urllib.request, json, sys
url = 'http://127.0.0.1:8000/api/commandes/vendeur/commandes/mes_commandes/'
req = urllib.request.Request(url, headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzg2MTA3MzI5LCJpYXQiOjE3ODYxMDcwMjksImp0aSI6IjhhMjRjYmRmMDc0YjRiZGZhNTNlZTlhNDdjODJlMDAzIiwidXNlcl9pZCI6IjE1In0.HyirtKOcQeRCDC3tsBrxj5e1CKjwUN1mPXYryVjYDfo'})
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode())
