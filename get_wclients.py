import json
import requests
import platform                 # for getting the operating system name
import sys
from pprint import pprint


# check if scirpt is executed on linux system
if platform.system().lower() != 'linux':
    print(f'ERROR\nThis scrpit work only on Linux systemes')
    sys.exit()
else:
    from tabulate import tabulate   # for formating print results


def get_user_input(message, error_message):
    # collect user input and make sure it is not blank
    x = input(message)
    while len(x.strip()) == 0:
        x = input(error_message)
    return x

def check_user_input_number(user_input, all_org_list):
    # check if user input is number and in valid range
    try:
        int(user_input)
        if int(user_input) <= 0 or int(user_input) > len(all_org_list):
            return False
        else:
            return True
    except ValueError:
        return False

def api_request(url):
    try:                                                    # try to send API call
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:            # in case of error exit out from script
        raise SystemExit(err)

def get_all_organizations():
    # using API key, get all availbe organizations
    print(f'Collecting all organization names:')
    url = f'https://dashboard.meraki.com/api/v0/organizations/'
    response_json = api_request(url)
    return response_json


def print_organization_name(all_org):
    # print all organizatin names to the screen, user will chose one in get_organization_id
    counter = 1
    for org in all_orgs:
        print(f"{counter}) {org['name']}")
        counter += 1

def get_organization_id(all_org_list):
    # get organization id for organization user chose
    organization_number = get_user_input('\nChose Organization (number) from the list: ', \
    'Input cannot be empty. Chose a number: ')         # collect organization name for user input
    
    # check if users has eneterd valid number and if yes return org id
    if check_user_input_number(organization_number, all_org_list) == False:
        get_organization_id(all_org_list)
    else:
        return all_org_list[int(organization_number)-1]['id']


def get_networks(org_id):
    # get all network names and ids, save the result to the list
    print(f'Collecting Networks')
    url = f'https://dashboard.meraki.com/api/v0/organizations/{org_id}/networks'
    response_json = api_request(url)
    
    networks = []
    for network in response_json:
        tmp_dict = {}
        tmp_dict["id"] = network['id']
        tmp_dict["name"] = network['name']
        networks.append(tmp_dict)

    return(networks)

def get_all_clients(networks):
    # get all connected clients in last 60 minutes
    all_clients = []
    for network in networks:
        tmp_dict = {}
        print(f"Collecting information for {network['name']}")
        url = f"https://api.meraki.com/api/v1/networks/{network['id']}/clients/?perPage=200&timespan=10800"
        response_json = api_request(url)
        tmp_dict['name'] = network['name']
        tmp_dict['clients'] = response_json
        
        all_clients.append(tmp_dict)            # add results from every network to all_clients list           

    return all_clients

def wireless_clients(all_clients_list):
    all_wireless_clients = []
    for location in all_clients_list:
        for client in location['clients']:
            tmp_list = []
            if client['ssid'] != None:
                tmp_list.append(location['name'])
                tmp_list.append(client['status'])
                tmp_list.append(client['ssid'])
                tmp_list.append(client['mac'])
                tmp_list.append(client['os'])
                tmp_list.append(client['description'])
            if tmp_list:
                all_wireless_clients.append(tmp_list)
    
    return all_wireless_clients



def print_results(results_list):
    # print to cosole information gathered in def get_data_print
    print(tabulate(results_list, headers=['Location', 'Status', 'SSID', 'MAC Address', 'Device Type, OS', 'Endpoint Description']))

# get user input
key = get_user_input('Enter Meraki API key: ', \
    'Input cannot be empty. Enter API key: ')                   # collect API key for user input     


# format console output
print('-' * 20 + '\n')

# prepare http headers
headers = {'X-Cisco-Meraki-API-Key': key}

all_orgs = get_all_organizations()                                  # get all organizations
print_organization_name(all_orgs)                                   # print organizations
org_id = get_organization_id(all_orgs)                              # get organization id

# format console output
print('-' * 20 + '\n')
networks = get_networks(org_id)                                     # get networks
all_clients = get_all_clients(networks)
all_wireless_clients = wireless_clients(all_clients)
sorted_wireless_clients = sorted(all_wireless_clients, key=lambda x: x[2])

# format console output
print('-' * 20 + '\n')

print_results(sorted_wireless_clients)



