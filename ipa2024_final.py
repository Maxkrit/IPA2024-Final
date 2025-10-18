#######################################################################################
# Yourname:
# Your student ID:
# Your GitHub Repo: 

#######################################################################################
# 1. Import libraries for API requests, JSON formatting, time, os, (restconf_final or netconf_final), netmiko_final, and ansible_final.

import requests
import json
import time
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder

import ansible_final
import restconf_final
import netmiko_final

#######################################################################################
# 2. Assign the Webex accesssetx WEBEX_TOKEN "OGFmNzY3MjMtMzM5OS00MTYwLThkM2QtYTBmN2EzZGQ4YmQ1YTA1YWFkNzktMDRh_PS65_e37c9b35-5d15-4275-8997-b5c6f91a842d"

ACCESS_TOKEN = os.environ["token"]

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vN2Q0Nzk0MDAtYWFiOS0xMWYwLWIyMjEtM2Q0YjM3Nzk0OTVl"
)
router_ip = "10.0.15.63"
last_message_id = None  # เก็บ ID ของข้อความล่าสุดที่เราอ่านแล้ว

def json_to_cli(data):
    cli = []

    # hostname
    if "hostname" in data:
        cli.append(f"hostname {data['hostname']}")
        cli.append("!")

    # username
    if "username" in data:
        for u in data["username"]:
            pwd = u["password"]["password"]
            cli.append(f"username {u['name']} privilege {u['privilege']} password {pwd}")
        cli.append("!")

    # ip domain name
    if "ip" in data and "domain" in data["ip"]:
        cli.append(f"ip domain name {data['ip']['domain']['name']}")
        cli.append("!")

    # ssh
    if "ip" in data and "ssh" in data["ip"]:
        cli.append(f"ip ssh version {data['ip']['ssh']['version']}")
        cli.append("!")

    # HTTP server
    http = data["ip"].get("Cisco-IOS-XE-http:http", {})
    if http.get("server"):
        cli.append("ip http server")
    if http.get("secure-server"):
        cli.append("ip http secure-server")
    cli.append("!")

    # ntp
    if "ntp" in data and "Cisco-IOS-XE-ntp:server" in data["ntp"]:
        for s in data["ntp"]["Cisco-IOS-XE-ntp:server"]["server-list"]:
            cli.append(f"ntp server {s['ip-address']}")
        cli.append("!")

    # interfaces
    if "interface" in data:
        for intf_type, intfs in data["interface"].items():
            for intf in intfs:
                cli.append(f"interface {intf_type}{intf['name']}")
                if intf.get("description"):
                    cli.append(f" description {intf['description']}")
                if intf.get("ip") and intf["ip"].get("address"):
                    primary = intf["ip"]["address"]["primary"]
                    cli.append(f" ip address {primary['address']} {primary['mask']}")
                if intf.get("shutdown") is not None:
                    cli.append(" shutdown")
                cli.append("!")

    return "\n".join(cli)


while True:
    # always add 1 second of delay to the loop to not go over a rate limit of API calls
    time.sleep(1)

    # the Webex Teams GET parameters
    #  "roomId" is the ID of the selected room
    #  "max": 1  limits to get only the very last message in the room
    getParameters = {"roomId": roomIdToGetMessages, "max": 1}

    
    # the Webex Teams HTTP header, including the Authoriztion
    getHTTPHeader = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

# 4. Provide the URL to the Webex Teams messages API, and extract location from the received message.
    
    # Send a GET request to the Webex Teams messages API.
    # - Use the GetParameters to get only the latest message.
    # - Store the message in the "r" variable.
    r = requests.get(
        "https://webexapis.com/v1/messages",
        params=getParameters,
        headers=getHTTPHeader,
    )
    # verify if the retuned HTTP status code is 200/OK
    if not r.status_code == 200:
        raise Exception(
            "Incorrect reply from Webex Teams API. Status code: {}".format(r.status_code)
        )

    # get the JSON formatted returned data
    messages = r.json().get("items", [])
    if not messages:
        continue

    message = messages[0]
    message_id = message["id"]
    message_text = message["text"].strip()

    if not message_text.startswith("/66070007"):
        continue
    
    if message_id == last_message_id:
        continue

    print("Received message:", message_text)
    last_message_id = message_id

    # แยก student_id และ command
    parts = message_text.lstrip("/").split()
    student_id = parts[0]
    command = " ".join(parts[1:]) if len(parts) > 1 else ""

# 5. Complete the logic for each command

    responseMessage = ""
    # ตรวจสอบว่าข้อความนี้เราอ่านแล้วหรือยัง
    if command == ("create"):
        restconf_final.create(student_id, roomIdToGetMessages, ACCESS_TOKEN)
    elif command == "delete":
        restconf_final.delete(student_id, roomIdToGetMessages, ACCESS_TOKEN)
    elif command == "enable":
        restconf_final.enable(student_id, roomIdToGetMessages, ACCESS_TOKEN)
    elif command == "disable":
        restconf_final.disable(student_id, roomIdToGetMessages, ACCESS_TOKEN)
    elif command == "status":
        restconf_final.status(student_id,router_ip, roomIdToGetMessages, ACCESS_TOKEN)
    elif command == "gigabit_status":
        status_text = netmiko_final.gigabit_status()  # ดึงสถานะ interfaces

        # ส่งข้อความกลับ Webex
        postData = json.dumps({
            "roomId": roomIdToGetMessages,
            "text": f"{status_text}"
        })

        HTTPHeaders = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://webexapis.com/v1/messages",
            data=postData,
            headers=HTTPHeaders
        )

        if response.status_code == 200:
            print("✅ Status sent to Webex!")
        else:
            print("❌ Failed to send message:", response.text)
    else:
        
# 6. Complete the code to post the message to the Webex Teams room.

        # The Webex Teams POST JSON data for command showrun
        # - "roomId" is is ID of the selected room
        # - "text": is always "show running config"
        # - "files": is a tuple of filename, fileobject, and filetype.

        # the Webex Teams HTTP headers, including the Authoriztion and Content-Type
        
        # Prepare postData and HTTPHeaders for command showrun
        # Need to attach file if responseMessage is 'ok'; 
        # Read Send a Message with Attachments Local File Attachments
        # https://developer.webex.com/docs/basics for more detail


    
#  and responseMessage == "ok"
        if command == "showrun":
            
            # เรียกฟังก์ชัน showrun จาก ansible_final
            responseMessage, ansible_output = ansible_final.showrun(router_ip, student_id)

            if responseMessage == "fuck":
                # ถ้า responseMessage เป็น "fuck" จะไม่ทำอะไร (หรือจะแสดงข้อความเฉพาะก็ได้)
                print("Response is 'fuck' — ไม่ส่งไฟล์ไป Webex")
                
            else:
                # ✅ เขียนผลลัพธ์ลงไฟล์ใหม่
                filename = f"{student_id}_running_config.txt"
                myfile = f"{student_id}_runningconfig_router.txt"
                with open(filename, "w") as f:
                    f.write(ansible_output)

                # ✅ เปิดไฟล์เพื่อแนบส่งไป Webex
                with open(myfile, "rb") as f:
                    fileobject = f.read()

                # ✅ เตรียม multipart form สำหรับส่งไฟล์ไป Webex

                myfile = f"{student_id}_runningconfig_router.txt"
                postData = MultipartEncoder(
                    fields={
                        "roomId": roomIdToGetMessages,
                        "text": f"show running config",
                        "files": (myfile, fileobject, "text/plain")
                    }
                )

                HTTPHeaders = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": postData.content_type
                }

                # ✅ ส่งไฟล์ไป Webex
                response = requests.post(
                    "https://webexapis.com/v1/messages",
                    data=postData,
                    headers=HTTPHeaders
                )

                print(f"ส่งไฟล์ {filename} ไปยัง Webex เรียบร้อยแล้ว ✅")