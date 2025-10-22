import requests
import base64

requests.packages.urllib3.disable_warnings()


# Router IP Address is 10.0.15.181-184

# the RESTCONF HTTP headers, including the Accept and Content-Type
# Two YANG data formats (JSON and XML) work with RESTCONF 
headers = {
    "Accept": "application/yang-data+json",      # รับข้อมูล JSON
    "Content-Type": "application/yang-data+json" # ส่งข้อมูล JSON
}

basicauth = ("admin", "cisco")
BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()

def create(student_id, router_ip, room_id, access_token):
    import requests
    import base64
    import json

    basicauth = ("admin", "cisco")
    BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()

    loopback_num = int(student_id[-3:])  # last 3 digits as number
    x = loopback_num // 100
    y = loopback_num % 100
    ip_addr = f"172.{x}.{y}.1"


    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"

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
        text_to_send = f"Interface loopback {student_id} is created successfully"
    else:
        text_to_send = f"Cannot create: Interface loopback {student_id}"

    postData = json.dumps({
        "roomId": room_id,
        "text": text_to_send
    })

    HTTPHeaders = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    requests.post("https://webexapis.com/v1/messages", data=postData, headers=HTTPHeaders)


def delete(student_id, router_ip, room_id, access_token):
    import requests
    import base64
    import json

    basicauth = ("admin", "cisco")
    BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()

    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"

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
        text_to_send = f"Cannot delete: Interface loopback {student_id}"

    postData = json.dumps({
        "roomId": room_id,
        "text": text_to_send
    })
    HTTPHeaders = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    requests.post("https://webexapis.com/v1/messages", data=postData, headers=HTTPHeaders)

def enable(student_id, router_ip, room_id, access_token):
    import requests
    import base64
    import json

    # ตั้งค่า Basic Auth สำหรับ RESTCONF
    basicauth = ("admin", "cisco")
    BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()

    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"

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
            HTTPHeaders = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
            requests.post("https://webexapis.com/v1/messages", data=postData, headers=HTTPHeaders)
            return

    # ถ้ามีอยู่ให้ enable (no shutdown)
    payload = {
        "ietf-interfaces:interface": {
            "name": f"Loopback{student_id}",
            "enabled": True
        }
    }

    url_patch = f"{api_url}/interface=Loopback{student_id}"
    response = requests.patch(url_patch, headers=headers, json=payload, verify=False)

    if response.status_code in [200, 204]:
        text_to_send = f"Interface loopback {student_id} is enable successfully"
    else:
        text_to_send = f"Cannot enable: Interface loopback {student_id}"

    postData = json.dumps({
        "roomId": room_id,
        "text": text_to_send
    })
    HTTPHeaders = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    requests.post("https://webexapis.com/v1/messages", data=postData, headers=HTTPHeaders)


def disable(student_id, router_ip, room_id, access_token):
    basicauth = ("admin", "cisco")
    BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()
    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
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
                text_to_send = f"Interface loopback {student_id} is shutdowned successfully"
            else:
                text_to_send = f"Cannot shutdown: Interface loopback {student_id}"
    except Exception as e:
        text_to_send = f"Error disabling interface {interface_name}: {str(e)}"

    # ส่งข้อความกลับ Webex
    requests.post(
        "https://webexapis.com/v1/messages",
        json={"roomId": room_id, "text": text_to_send},
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    )

def status(student_id, router_ip, room_id, access_token):
    basicauth = ("admin", "cisco")
    BASIC_AUTH = base64.b64encode(f"{basicauth[0]}:{basicauth[1]}".encode()).decode()
    api_url = f"https://{router_ip}/restconf/data/ietf-interfaces:interfaces"
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
        matched_intf = next((intf for intf in interfaces if intf.get("name") == interface_name), None)

        if not matched_intf:
            text_to_send = f"No Interface {interface_name}"
        else:
            admin_status = matched_intf.get("enabled")
            print(admin_status)
            if admin_status == True:
                text_to_send = f"Interface {interface_name} is enabled"
            elif admin_status == False:
                text_to_send = f"Interface {interface_name} is disabled"
            else:
                text_to_send = f"Interface {interface_name} status unknown"

    except Exception as e:
        text_to_send = f"Error checking interface {interface_name}: {str(e)}"

    # ส่งข้อความกลับ Webex
    requests.post(
        "https://webexapis.com/v1/messages",
        json={"roomId": room_id, "text": text_to_send},
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    )