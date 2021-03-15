import requests
import sys

url = sys.argv.pop()

response = requests.get(url+"/book", params={'UID': 5})
print(response.status_code)
