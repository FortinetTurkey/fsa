import time
import requests
import zipfile, os, shutil, gzip
import syslog
import logging
from logging.handlers import SysLogHandler
import socket  # Add this import
import hashlib

def get_current_time():
    current_time = time.time()
    current_time = int(current_time)*1000
    time_minus_10 = current_time - 330000
    return time_minus_10


def create_hash(input_string):
    # Create a new sha256 hash object
    sha256_hash = hashlib.sha256()

    # Update the hash object with the bytes of the input string
    sha256_hash.update(input_string.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hash_hex = sha256_hash.hexdigest()

    return hash_hex

def main():
    swp = SWP()
    swp.download_and_save_zip()
    swp.unzip_and_remove()
    swp.read_file_and_send_syslog()

class SWP:
    def __init__ (self):
        self.APIUsername = '8ed0cedc-1343-42ec-90ed-4ded08f01a5e'
        self.X_APIPassword = '06eb1b8d-5c19-40ed-b082-9767e44cb90e'
        self.curl_str = 'https://portal.threatpulse.com/reportpod/logs/sync?startDate=0000000000000&endDate=0&token=none'
        self.filename = "tmp.zip"
        self.syslog_file = "tmp.log"

    def download_and_save_zip(self):
        url = self.curl_str
        time_tmp = get_current_time()
        url = url.replace('0000000000000', str(time_tmp))

        headers = {
            'X-APIUsername': self.APIUsername,
            'X-APIPassword': self.X_APIPassword
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        zip_path = './tmp/' + self.filename
        with open(zip_path, 'wb') as file:
            file.write(response.content)
        print(f"File saved to {zip_path}")

    def unzip_and_remove(self):
        # Unzip the main zip file
        with zipfile.ZipFile('./tmp/' + self.filename, 'r') as zip_ref:
            zip_ref.extractall('./tmp/')
        print("File unzipped")

        # Find the .log.gz file dynamically
        for file_name in os.listdir('./tmp'):
            if file_name.endswith('.log.gz'):
                gz_file_path = os.path.join('./tmp', file_name)
                log_file_path = gz_file_path[:-3]  # Remove the .gz extension

                # Unzip the .gz file
                with gzip.open(gz_file_path, 'rb') as f_in:
                    with open(log_file_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"Gz file {gz_file_path} unzipped to {log_file_path}")
                self.syslog_file = {log_file_path}
                self.syslog_file = str(self.syslog_file).replace('\'','').replace('{','').replace('}','')
                # Remove the .gz file
                os.remove(gz_file_path)
                print(f"Gz file {gz_file_path} deleted")

        # Remove the main zip file
        os.remove('./tmp/' + self.filename)
        print(f"Zip file {self.filename} deleted")

    def read_file_and_send_syslog(self):
        # Configure the logger to send messages to the remote syslog server
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        syslog_handler = SysLogHandler(address=('10.34.1.92', 514))
        formatter = logging.Formatter('%(message)s')
        syslog_handler.setFormatter(formatter)
        logger.addHandler(syslog_handler)
        last_line_hash = ''
        # Read the log file and send its contents as syslog messages
        with open(self.syslog_file, 'r') as log_file:
            for line in log_file:
                logger.info(" BluecoatWebCloud " +line.strip())
                last_line_hash = create_hash(line.strip())

        with open('last_hash.txt', 'w') as hash_file:
            hash_file.write(last_line_hash)

        print(f"Log file {self.syslog_file} sent as syslog messages to remote server")

    def create_hash(input_string):
        # Create a new sha256 hash object
        sha256_hash = hashlib.sha256()

        # Update the hash object with the bytes of the input string
        sha256_hash.update(input_string.encode('utf-8'))

        # Get the hexadecimal representation of the hash
        hash_hex = sha256_hash.hexdigest()

        return hash_hex
if __name__ == "__main__":
    main()
