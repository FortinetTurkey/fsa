import base64
import requests
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

fsa_url = "https://10.34.1.80/jsonrpc"

def login1():
    req = {"method": "get", "params": [ { "url": "/sys/login/token","token": "R9JyZkdTFRdHpYFV"}], "session": "", "id": 53,"ver": "2.5" }
    r = requests.post(url=fsa_url, json=req, verify=False)
    sid = r.json()["session"]
    print("Step: Login")
    print("Token: " + sid)
    print("------------------------")
    return sid


def login():
    username = "admin"
    password = "Pass1234"
    req = {"id": 1, "method": "exec","params": [{"passwd": password, "user": username, "url": "/sys/login/user"}]}
    r = requests.post(url=fsa_url, json=req, verify=False)
    print(r.json())
    sid = r.json()["session"]
    return sid
    
def logout(sid):
    req = {"id": 1, "method": "exec", "params": [{"url": "/sys/logout"}], "session": sid}
    r = requests.post(url=fsa_url, json=req, verify=False)
    print("Step: Logout")
    print(r.json())
    print("------------------------")


def file_to_base64(file_path):
    try:
        # Read the file contents in binary mode
        with open(file_path, 'rb') as file:
            binary_data = file.read()

        # Encode the binary data to Base64
        base64_encoded = base64.b64encode(binary_data)

        # Convert the bytes object to a string (if needed)
        base64_encoded_str = base64_encoded.decode('utf-8')

        return base64_encoded_str

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
def upload_file(sid, filename):

    input_bytes = filename.encode('utf-8')
    base64_encoded = base64.b64encode(input_bytes)
    base64_encoded_str = base64_encoded.decode('utf-8')

    #print(base64_encoded_str)

    file_data = file_to_base64("windows.exe")

    req = {
      "id": 11,
      "method": "set",
      "params": [
        {
          "comments": "this is test file from rpc",
          "enable_ai": 1,
          "file": file_data,
          "filename": base64_encoded_str,
          "forcedvm": 1,
          "overwrite_vm_list": "WIN7X86VMO16E",
          "skip_steps": "",
          "timeout": "3600",
          "type": "file",
          "url": "/alert/ondemand/submit-file",
          "vrecord": 0
        }
      ],
      "session": sid,
      "ver": "4.2.1"
    }

    res = requests.post(url=fsa_url, json=req, verify=False)
    print(res.json())

def upload_url(sid, submit_url):

    input_bytes = submit_url.encode('utf-8')
    base64_encoded = base64.b64encode(input_bytes)
    base64_encoded_str = base64_encoded.decode('utf-8')

    tmp_name = "scan_of_" + submit_url
    input_bytes = tmp_name.encode('utf-8')
    base64_encoded = base64.b64encode(input_bytes)
    name_base64_encoded_str = base64_encoded.decode('utf-8')    
    
    #print(base64_encoded_str)

    file_data = file_to_base64("windows.exe")

    req = {
        "id": 12,
        "method": "set",
        "params": [{
            "depth": "3",
            "file": base64_encoded_str,
            "filename": name_base64_encoded_str,
            "timeout": "60",
            "type": "url",
            "url": "/alert/ondemand/submit-file"
            }
            ],
        "session": sid,
        "ver": "2.0"
    }

    res = requests.post(url=fsa_url, json=req, verify=False)
    print(res.json())

def submit_file_on_demand(filename):
    sid = login()
    upload_file(sid, filename)
    logout(sid)

def submit_url_on_demand(submit_url):
    sid = login()
    upload_url(sid, submit_url)
    logout(sid)

submit_file = "windows.exe"
submit_file_on_demand(submit_file)

#submit_url = "https://secure.eicar.org/eicar_com.zip"
#submit_url_on_demand(submit_url)