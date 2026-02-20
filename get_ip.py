import requests
try:
    ip = requests.get('https://api.ipify.org').text
    print(f"Your Public IP: {ip}")
except:
    print("Could not get IP")
