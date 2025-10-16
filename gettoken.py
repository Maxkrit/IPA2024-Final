import os
import requests

ACCESS_TOKEN = os.environ.get("WEBEX_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    print("❌ ไม่พบโทเคน Webex กรุณาตั้งค่า WEBEX_ACCESS_TOKEN")
    exit()

# URL สำหรับดึงข้อมูลผู้ใช้ปัจจุบัน
url = "https://webexapis.com/v1/people/me"

# ตั้ง headers พร้อม Authorization
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# ส่งคำขอ GET
response = requests.get(url, headers=headers)

# ตรวจสอบผลลัพธ์
if response.status_code == 200:
    data = response.json()
    print("✅ โทเคนใช้ได้! ชื่อผู้ใช้ Webex ของคุณคือ:", data.get("displayName"))
else:
    print(f"❌ โทเคนไม่ถูกต้องหรือหมดอายุ! Status code: {response.status_code}")
    print("รายละเอียด:", response.text)
