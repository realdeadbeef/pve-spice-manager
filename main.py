import requests
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from configparser import ConfigParser
from time import sleep

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

current_version = '1.0'

# GitHub version checking
latest_version = requests.get("https://api.github.com/repos/realdeadbeef/pve-spice-manager/releases/latest")
latest_version = str(latest_version.json()["tag_name"])

if latest_version != current_version:
    print(f'Your version of pve-spice-manager has been outdated by {latest_version}.\nPlease update for the latest '
          f'bug fixes and improvements from: https://github.com/realdeadbeef/pve-spice-manager/releases\n')

dir_path = f"{os.environ['APPDATA']}\\pve-spice-manager"
pools = []
pool_member_names = []
pool_member_id = []
pool_member_node = []

# check if config exists
if not os.path.isdir(dir_path):
    os.mkdir(dir_path)
if not os.path.isfile(f'{dir_path}\\config.ini'):
    config_obj = ConfigParser()

    config_obj["PVE"] = {
        "username": "user@realm",
        "password": "P4ssw0rd",
        "proxy": "0.0.0.0",
        "port": "8006"
    }

    with open(f'{dir_path}\\config.ini', 'w') as conf:
        config_obj.write(conf)

    print(f"Config file has been created, please make your changes to {dir_path}\\config.ini and re-run the executable")

    while True:
        openScript = str(input('Would you like the script to attempt to open the file now? (y/n) '))

        if openScript.lower() == 'y':
            os.startfile(f'{dir_path}\\config.ini')
            break
        elif openScript.lower() == 'n':
            input('Press ENTER to exit...')
            break
        else:
            print('Invalid choice, please type y or n')
            sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')
    exit(0)

config_object = ConfigParser()
config_object.read(f'{dir_path}\\config.ini')

PVE_config_data = config_object['PVE']
username = PVE_config_data['username']
password = PVE_config_data['password']
proxy = PVE_config_data['proxy']
port = PVE_config_data['port']

# define username and password used to authenticate and obtain ticket -- then obtain ticket
ticket_creds = {'username': username, 'password': password}
ticket_raw = requests.post(f'https://{proxy}:{port}/api2/json/access/ticket', params=ticket_creds, verify=False)
if ticket_raw.status_code != 200:
    print(f'Error fetching ticket (HTTP Error: {ticket_raw.status_code})')
    input('Press ENTER to continue...')
    exit(1)
ticket_response = ticket_raw.json()

# store ticket and CSRF prevention token in variables
PVE_ticket = (ticket_response['data']['ticket'])
CSRF_prev_token = (ticket_response['data']['CSRFPreventionToken'])

# turn the above-mentioned variables into a cookie and some headers
PVE_auth_cookie = dict(PVEAuthCookie=PVE_ticket)
PVE_auth_headers = {'CSRFPreventionToken': CSRF_prev_token}

# obtain a list of pools
pools_raw = requests.get(f'https://{proxy}:{port}/api2/json/pools', headers=PVE_auth_headers, cookies=PVE_auth_cookie,
                         verify=False)
if pools_raw.status_code != 200:
    print(f'Error fetching pools (HTTP Error: {pools_raw.status_code})')
    input('Press ENTER to continue...')
    exit(1)
pools_response = pools_raw.json()

# store the pools in an array and ask the user which one they would like to choose from
pools.extend(item['poolid'] for item in pools_response['data'])
while True:
    print('Select a pool:\n')
    for item in pools:
        print(f'{pools.index(item)}) {item}')
    try:
        vm_pool = pools[int(input('==> '))]
        os.system('cls' if os.name == 'nt' else 'clear')
        break
    except:
        print('No such pool\n')
        sleep(2)
        os.system('cls' if os.name == 'nt' else 'clear')

# get members of selected pool
pool_data_raw = requests.get(f'https://{proxy}:{port}/api2/json/pools/{vm_pool}', headers=PVE_auth_headers,
                             cookies=PVE_auth_cookie, verify=False)
if pool_data_raw.status_code != 200:
    print(f'Error fetching pool data (HTTP Error: {pool_data_raw.status_code})')
    input('Press ENTER to continue...')
    exit(1)
pool_data_response = pool_data_raw.json()

# store the names and id's of the vms and what node they are located on
pool_member_names.extend(
    item['name'] for item in pool_data_response['data']['members']
)

pool_member_id.extend(
    item['vmid'] for item in pool_data_response['data']['members']
)

pool_member_node.extend(
    item['node'] for item in pool_data_response['data']['members']
)

# choose the node
while True:
    print('Select a VM:\n')
    for i in range(len(pool_member_id)):
        print(f'{pool_member_id[i]}) {pool_member_names[i]}')
    vmid = int(input('==> '))
    if vmid in pool_member_id:
        break
    print('No such VM')
    sleep(2)
    os.system('cls' if os.name == 'nt' else 'clear')
node = pool_member_node[pool_member_id.index(vmid)]

# get the contents of the spice file
SPICE_data_raw = requests.post(f'https://{proxy}:{port}/api2/spiceconfig/nodes/{node}/qemu/{vmid}/spiceproxy',
                               headers=PVE_auth_headers, cookies=PVE_auth_cookie, data={'proxy': proxy}, verify=False)
if SPICE_data_raw.status_code != 200:
    print(f'Error fetching spice file (HTTP Error: {SPICE_data_raw.status_code})')
    input('Press ENTER to continue...')
    exit(1)
SPICE_data_response = SPICE_data_raw.text

# write the contents of the spice file to a virt-viewer file
with open(f'{dir_path}{vmid}-{node}.vv', 'w') as spice_file:
    spice_file.write(SPICE_data_response)
spice_file_location = f'{dir_path}{vmid}-{node}.vv'

# open the spice file with the default application
os.startfile(spice_file_location)
