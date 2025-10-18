import subprocess

def showrun(router_ip, student_id):
    command = [
        "ansible-playbook",
        "showrun.yml",
        "-i", "hosts.ini",
        "--extra-vars",
        f"router_ip=10.0.15.63 student_id={student_id}"
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    output = result.stdout + "\n" + result.stderr

    if "FAILED" in output or "unreachable" in output:
        return "ok", output
    else:
        return "mai ok"
