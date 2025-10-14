import socket
try:
    print(socket.gethostbyname('login.microsoftonline.com'))
except Exception as e:
    print("DNS error:", e)



import requests
try:
    r = requests.get('https://login.microsoftonline.com/.well-known/openid-configuration', timeout=8)
    print("HTTP status:", r.status_code)
except Exception as e:
    print("HTTP error:", e)



import os
print("HTTP_PROXY:", os.environ.get('HTTP_PROXY'))
print("HTTPS_PROXY:", os.environ.get('HTTPS_PROXY'))
