import subprocess
import time
import requests
from bs4 import BeautifulSoup

# Start server
p = subprocess.Popen(['.venv/bin/python', 'manage.py', 'runserver', '8001'])
time.sleep(2)

try:
    # 1. Get the landing page to get CSRF token
    client = requests.Session()
    r = client.get('http://127.0.0.1:8001/')
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
    
    # 2. Make the POST request
    payload = {
        'csrfmiddlewaretoken': csrf_token,
        'email': 'naglesnora7@gmail.com',
        'diagnosis': '{"scores":{"num":2,"dat":2,"nar":0},"capital":"inv","recommendation":"Pitch Lab","answers":[2,0,2,0,"inv"]}'
    }
    r2 = client.post('http://127.0.0.1:8001/blog/suscribirme/', data=payload, headers={'Accept': 'application/json', 'Referer': 'http://127.0.0.1:8001/'})
    print("STATUS CODE:", r2.status_code)
    print("RESPONSE BODY:", r2.text)
finally:
    p.terminate()
