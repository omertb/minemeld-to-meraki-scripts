import requests
import json
import os
import sys
from time import gmtime, strftime

LOG_DIR = "/home/security/Scripts/Minemeld/DA365AzureIPRange/logs/"
DATE_FORMAT = "[%a, %d/%b/%Y %H:%M:%S +0000]"
NAME_FORMAT = "%Y%m%d.log"


requests.packages.urllib3.disable_warnings()
AZURE_JSON = "https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20210329.json"


def send_wr_log(log_message):
    # write to a log file
    log_date = strftime(DATE_FORMAT, gmtime())
    log_line = "{} - {}".format(log_date, log_message)
    log_filename = "{}{}".format(LOG_DIR, strftime(NAME_FORMAT, gmtime()))
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    with open(log_filename, "a") as f:
        f.write("\n" + log_line)


def get_azure_json():
    response = requests.request(method="GET", url=AZURE_JSON, verify=False)
    if response.status_code != 200 or response.text == "":
        send_wr_log("Error while getting azure json from download.microsoft.com")
        sys.exit(-1)
    return response.text


def convert_json_to_ip_list():
    azure_ips_json = get_azure_json()
    azure_ips_dict = json.loads(azure_ips_json)
    values_list = azure_ips_dict['values']
    azure_west_europe = [item for item in values_list if item['name'].lower().endswith("westeurope")]
    address_list = ""
    for item in azure_west_europe:
        for address in item["properties"]["addressPrefixes"]:
            address_list = address_list + address + "\n"
    return address_list.rstrip("\n")


def main():
    ip_list = convert_json_to_ip_list()
    filename = "azurecloud.westeurope.txt"
    os.chdir("/home/security/Scripts/Minemeld/DA365AzureIPRange")

    with open(filename, "r") as f:
        previous_file = f.read()

    previous_ip_list = previous_file.splitlines()
    if sorted(set(ip_list)) == sorted(set(previous_ip_list)):
        send_wr_log("Azure IP List did not change! Exiting without processing")
        sys.exit(-1)
    else:
        send_wr_log("Azure IP List changed!. Updating file.")

    with open(filename, "w") as f:
        f.write(ip_list)


if __name__ == "__main__":
    main()
