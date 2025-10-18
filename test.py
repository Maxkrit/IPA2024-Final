import requests, os

ACCESS_TOKEN = os.environ.get("token")  # ใช้ environment variable
print("ACCESS_TOKEN =", ACCESS_TOKEN)

headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
url = "https://webexapis.com/v1/rooms"

response = requests.get(url, headers=headers)

print("Status:", response.status_code)
print("Response:", response.text)
