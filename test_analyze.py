import requests

url = "http://127.0.0.1:5000/analyze"
with open('anji.jpg.png', 'rb') as f:
    img_data = f.read()
files = {'image': ('anji.jpg.png', img_data, 'image/png')}
data = {'user_id': '1'}


try:
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
