import base64
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FSA_URL = "https://10.34.1.80/jsonrpc"
USERNAME = "admin"
PASSWORD = "Pass1234"

def login():
    req = {
        "id": 1,
        "method": "exec",
        "params": [{"passwd": PASSWORD, "user": USERNAME, "url": "/sys/login/user"}]
    }
    response = requests.post(url=FSA_URL, json=req, verify=False)
    response_data = response.json()
    print(response_data)
    return response_data["session"]

def logout(session_id):
    req = {
        "id": 1,
        "method": "exec",
        "params": [{"url": "/sys/logout"}],
        "session": session_id
    }
    response = requests.post(url=FSA_URL, json=req, verify=False)
    print("Step: Logout")
    print(response.json())
    print("------------------------")

def file_to_base64(file_path):
    try:
        with open(file_path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error: {e}")

def upload_file(session_id, filename):
    file_data = file_to_base64("windows.exe")
    req = {
        "id": 11,
        "method": "set",
        "params": [{
            "comments": "this is test file from rpc",
            "enable_ai": 1,
            "file": file_data,
            "filename": base64.b64encode(filename.encode('utf-8')).decode('utf-8'),
            "forcedvm": 1,
            "overwrite_vm_list": "WIN7X86VMO16E",
            "timeout": "3600",
            "type": "file",
            "url": "/alert/ondemand/submit-file",
            "vrecord": 0
        }],
        "session": session_id,
        "ver": "4.2.1"
    }
    response = requests.post(url=FSA_URL, json=req, verify=False)
    print(response.json())

def upload_url(session_id, submit_url):
    encoded_url = base64.b64encode(submit_url.encode('utf-8')).decode('utf-8')
    encoded_filename = base64.b64encode(f"scan_of_{submit_url}".encode('utf-8')).decode('utf-8')
    req = {
        "id": 12,
        "method": "set",
        "params": [{
            "depth": "3",
            "file": encoded_url,
            "filename": encoded_filename,
            "timeout": "60",
            "type": "url",
            "url": "/alert/ondemand/submit-file"
        }],
        "session": session_id,
        "ver": "2.0"
    }
    response = requests.post(url=FSA_URL, json=req, verify=False)
    print(response.json())

def submit_file_on_demand(filename):
    session_id = login()
    upload_file(session_id, filename)
    logout(session_id)

def submit_url_on_demand(submit_url):
    session_id = login()
    upload_url(session_id, submit_url)
    logout(session_id)

if __name__ == "__main__":
    submit_file_on_demand("windows.exe")
    # submit_url_on_demand("https://secure.eicar.org/eicar_com.zip")
