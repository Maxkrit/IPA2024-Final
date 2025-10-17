import requests
import json
import base64
import subprocess
import tempfile
import os

requests.packages.urllib3.disable_warnings()


# Router IP Address is 10.0.15.181-184
router_ip = "10.0.15.61"  # เปลี่ยนตาม Router ที่ต้องการ
api_url = f"https://{router_ip}/restconf/data/Cisco-IOS-XE-native:native"

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",      # รับข้อมูล JSON
    "Content-Type": "application/yang-data+json" # ส่งข้อมูล JSON
}

basicauth = ("admin", "cisco")
BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()

def create(student_id, room_id, access_token):
    import requests
    import base64
    import json

    basicauth = ("admin", "cisco")
    BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()

    loopback_num = int(student_id[-3:])  # last 3 digits as number
    x = loopback_num // 100
    y = loopback_num % 100
    ip_addr = f"172.{x}.{y}.1"


    api_url = "https://10.0.15.61/restconf/data/ietf-interfaces:interfaces"

    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json",
        "Authorization": f"Basic {BASIC_AUTH}"
    }

    # ตรวจสอบ interface ที่มีอยู่แล้ว
    get_response = requests.get(api_url, headers=headers, verify=False)
    if get_response.status_code == 200:
        interfaces = get_response.json().get("ietf-interfaces:interfaces", {}).get("interface", [])
        if any(intf.get("name") == f"Loopback{student_id}" for intf in interfaces):
            text_to_send = f"Loopback{student_id} already exists."
            postData = json.dumps({
                "roomId": room_id,
                "text": text_to_send
            })
            HTTPHeaders = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            requests.post("https://webexapis.com/v1/messages", data=postData, headers=HTTPHeaders)
            return

    # ถ้าไม่มีอยู่ สร้างใหม่
    payload = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{student_id}",
            "description": f"Loopback for student {student_id}",
            "type": "iana-if-type:softwareLoopback",
            "enabled": True,
            "ietf-ip:ipv4": {
                "address": [
                    {
                        "ip": ip_addr,
                        "netmask": "255.255.255.0"
                    }
                ]
            }
        }
    }


    response = requests.post(api_url, headers=headers, json=payload, verify=False)

    # ส่งผลลัพธ์กลับ Webex
    if response.status_code in [200, 201]:
        text_to_send = f"Created Loopback{student_id} with IP {ip_addr}"
    else:
        text_to_send = f"Failed to create Loopback{student_id}. Status: {response.status_code} {response.text}"

    postData = json.dumps({
        "roomId": room_id,
        "text": text_to_send
    })

    HTTPHeaders = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    requests.post("https://webexapis.com/v1/messages", data=postData, headers=HTTPHeaders)


def delete(student_id, room_id, access_token):
    import requests
    import base64
    import json

    basicauth = ("admin", "cisco")
    BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()

    api_url = f"https://10.0.15.61/restconf/data/ietf-interfaces:interfaces"

    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json",
        "Authorization": f"Basic {BASIC_AUTH}"
    }

    # ตรวจสอบ interface ที่มีอยู่แล้ว
    get_response = requests.get(api_url, headers=headers, verify=False)
    if get_response.status_code == 200:
        interfaces = get_response.json().get("ietf-interfaces:interfaces", {}).get("interface", [])
        if not any(intf.get("name") == f"Loopback{student_id}" for intf in interfaces):
            text_to_send = f"Interface loopback {student_id} does not exist."
            postData = json.dumps({
                "roomId": room_id,
                "text": text_to_send
            })
            HTTPHeaders = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            requests.post("https://webexapis.com/v1/messages", data=postData, headers=HTTPHeaders)
            return

    # ถ้ามีอยู่ให้ลบ
    url_delete = f"{api_url}/interface=Loopback{student_id}"
    response = requests.delete(url_delete, headers=headers, verify=False)

    if response.status_code in [200, 204]:
        text_to_send = f"Interface loopback {student_id} is deleted successfully"
    else:
        text_to_send = f"Failed to delete loopback {student_id}. Status: {response.status_code} {response.text}"

    postData = json.dumps({
        "roomId": room_id,
        "text": text_to_send
    })
    HTTPHeaders = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    requests.post("https://webexapis.com/v1/messages", data=postData, headers=HTTPHeaders)

def enable(student_id, room_id, access_token):
    basicauth = ("admin", "cisco")
    BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()
    api_url = "https://10.0.15.61/restconf/data/ietf-interfaces:interfaces"
    interface_name = f"Loopback{student_id}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json",
        "Authorization": f"Basic {BASIC_AUTH}"
    }

    try:
        # ตรวจสอบ interface
        get_response = requests.get(api_url, headers=headers, verify=False)
        interfaces = get_response.json().get("ietf-interfaces:interfaces", {}).get("interface", [])
        if not any(intf.get("name") == interface_name for intf in interfaces):
            text_to_send = f"Interface {interface_name} does not exist."
        else:
            # Enable interface
            url_patch = f"{api_url}/interface={interface_name}"
            payload = {"ietf-interfaces:interface": {"enabled": True}}
            resp = requests.patch(url_patch, headers=headers, json=payload, verify=False)
            if resp.status_code in [200, 204]:
                text_to_send = f"Interface {interface_name} is enabled successfully"
            else:
                text_to_send = f"Failed to enable interface {interface_name}. Status: {resp.status_code} {resp.text}"
    except Exception as e:
        text_to_send = f"Error enabling interface {interface_name}: {str(e)}"

    # ส่งข้อความกลับ Webex
    requests.post(
        "https://webexapis.com/v1/messages",
        json={"roomId": room_id, "text": text_to_send},
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    )


def disable(student_id, room_id, access_token):
    basicauth = ("admin", "cisco")
    BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()
    api_url = "https://10.0.15.61/restconf/data/ietf-interfaces:interfaces"
    interface_name = f"Loopback{student_id}"
    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json",
        "Authorization": f"Basic {BASIC_AUTH}"
    }

    try:
        # ตรวจสอบ interface
        get_response = requests.get(api_url, headers=headers, verify=False)
        interfaces = get_response.json().get("ietf-interfaces:interfaces", {}).get("interface", [])
        if not any(intf.get("name") == interface_name for intf in interfaces):
            text_to_send = f"Interface {interface_name} does not exist."
        else:
            # Disable interface
            url_patch = f"{api_url}/interface={interface_name}"
            payload = {"ietf-interfaces:interface": {"enabled": False}}
            resp = requests.patch(url_patch, headers=headers, json=payload, verify=False)
            if resp.status_code in [200, 204]:
                text_to_send = f"Interface {interface_name} is disabled successfully"
            else:
                text_to_send = f"Failed to disable interface {interface_name}. Status: {resp.status_code} {resp.text}"
    except Exception as e:
        text_to_send = f"Error disabling interface {interface_name}: {str(e)}"

    # ส่งข้อความกลับ Webex
    requests.post(
        "https://webexapis.com/v1/messages",
        json={"roomId": room_id, "text": text_to_send},
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    )

def status():
    print("status")
    # api_url_status = "<!!!REPLACEME with URL of RESTCONF Operational API!!!>"

    # resp = requests.<!!!REPLACEME with the proper HTTP Method!!!>(
    #     <!!!REPLACEME with URL!!!>, 
    #     auth=basicauth, 
    #     headers=<!!!REPLACEME with HTTP Header!!!>, 
    #     verify=False
    #     )

    # if(resp.status_code >= 200 and resp.status_code <= 299):
    #     print("STATUS OK: {}".format(resp.status_code))
    #     response_json = resp.json()
    #     admin_status = <!!!REPLACEME!!!>
    #     oper_status = <!!!REPLACEME!!!>
    #     if admin_status == 'up' and oper_status == 'up':
    #         return "<!!!REPLACEME with proper message!!!>"
    #     elif admin_status == 'down' and oper_status == 'down':
    #         return "<!!!REPLACEME with proper message!!!>"
    # elif(resp.status_code == 404):
    #     print("STATUS NOT FOUND: {}".format(resp.status_code))
    #     return "<!!!REPLACEME with proper message!!!>"
    # else:
    #     print('Error. Status Code: {}'.format(resp.status_code))

# ฟังก์ชันดึง show running config จาก router จริง ๆ
def showrun(student_id, room_id, access_token):
    import requests
    import base64
    import json

    router_ip = "10.0.15.61"
    basicauth = ("admin", "cisco")
    BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()

    api_url = f"https://{router_ip}/restconf/data/Cisco-IOS-XE-native:native"

    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
        "Authorization": f"Basic {BASIC_AUTH}"
    }

    try:
        # timeout ป้องกันการค้าง และ raise_for_status() ช่วยจับ error ทันที
        response = requests.get(api_url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()

        # แสดงผลใน console (debug)
        print(json.dumps(data, indent=2))

        # คืนค่า JSON data กลับให้ส่วนอื่นเรียกใช้ได้
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error fetching running config: {e}")
        return None

