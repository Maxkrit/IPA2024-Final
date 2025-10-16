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

# import restconf_final

#######################################################################################
# 2. Assign the Webex accesssetx WEBEX_TOKEN "OGFmNzY3MjMtMzM5OS00MTYwLThkM2QtYTBmN2EzZGQ4YmQ1YTA1YWFkNzktMDRh_PS65_e37c9b35-5d15-4275-8997-b5c6f91a842d"

ACCESS_TOKEN = os.environ["WEBEX_TOKEN"]

#######################################################################################
# 3. Prepare parameters get the latest message for messages API.

# Defines a variable that will hold the roomId
roomIdToGetMessages = (
    "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vN2Q0Nzk0MDAtYWFiOS0xMWYwLWIyMjEtM2Q0YjM3Nzk0OTVl"
)

last_message_id = None  # เก็บ ID ของข้อความล่าสุดที่เราอ่านแล้ว

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
        print("create")
    elif command == "delete":
        print("delete")
    elif command == "enable":
        print("enable")
    elif command == "disable":
        print("disable")
    elif command == "status":
        print("status")
    elif command == "gigabit_status":
        print("gigabit-status")
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
            filename = "show_running_config.txt"
            if not os.path.exists(filename):
                with open(filename, "w") as f:
                    f.write("helpme")

            with open(filename, "rb") as f:
                fileobject = f.read()

            postData = MultipartEncoder(
                fields={
                    "roomId": roomIdToGetMessages,
                    "text": "show running config",
                    "files": (filename, fileobject, "text/plain")
                }
            )

            HTTPHeaders = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": postData.content_type
            }
        else:
            responseMessage = "no command"
            text_to_send = responseMessage
            postData = json.dumps({
                "roomId": roomIdToGetMessages,
                "text": text_to_send
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
