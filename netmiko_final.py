from netmiko import ConnectHandler
from pprint import pprint

device_ip = "10.0.15.63"
username = "admin"
password = "cisco"

device_params = {
    "device_type": "cisco_ios",  # IOS XE ใช้ cisco_ios
    "ip": device_ip,
    "username": username,
    "password": password,
    "conn_timeout": 30,
    "banner_timeout": 30,
    "auth_timeout": 30,
    "global_delay_factor": 2,
    "fast_cli": False
}

def gigabit_status():
    try:
        print(f"🔌 Connecting to router {device_ip} ...")
        with ConnectHandler(**device_params) as ssh:
            # ปิด paging
            ssh.send_command("terminal length 0", expect_string=r"#")
            
            # ดึงสถานะ interfaces
            output = ssh.send_command("show ip interface brief", use_textfsm=True)
            
            up = 0
            down = 0
            admin_down = 0
            ans_list = []
            
            for intf in output:
                if intf['interface'].startswith("GigabitEthernet"):
                    ans_list.append(f"{intf['interface']} {intf['status']}")
                    if intf['status'] == "up":
                        up += 1
                    elif intf['status'] == "down":
                        down += 1
                    elif intf['status'] == "administratively down":
                        admin_down += 1

            summary = f"-> {up} up, {down} down, {admin_down} administratively down"
            output = ", ".join(ans_list) + " " + summary
            return output

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return str(e)
