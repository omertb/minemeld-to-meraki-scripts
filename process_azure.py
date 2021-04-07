#!/usr/bin/env python3

import requests
import sys
import time
import os
from logger import send_wr_log


COMMENT = "azure_westeurope_minemeld"
MAIN_DIR = '/nw/meraki/automation-scripts/update_meraki_rules'
AZURE_WEST_URL = "https://10.62.0.155/feeds/D365AzureIPRangeOutput"
requests.packages.urllib3.disable_warnings()


def get_azure_minemeld():
    os.chdir(MAIN_DIR)
    try:
        response = requests.request(method="GET", url=AZURE_WEST_URL, verify=False, timeout=15)
    except requests.exceptions.ConnectionError as e:
        send_wr_log("Connection Error: {}".format(str(e)))
        sys.exit(-1)
    except Exception as e:
        send_wr_log("Not handled exception: {}".format(str(e)))
        sys.exit(-1)

    if response.status_code != 200 or response.text == "":
        send_wr_log("Invalid response while getting IPv4 feed from minemeld! Code: {}".format(str(response.status_code)))
        sys.exit(-1)
    ip_addrs = response.text

    all_ip_list = ip_addrs.splitlines()
    ip_list = [ip for ip in all_ip_list if not ":" in ip]  # removed ipv6 addresses
    ip_addrs = "\n".join(ip_list)

    filename = "azure_westeurope_minemeld.txt"
    with open(filename, "r") as f:
        minemeld_file_content = f.read()

    minemeld_list = minemeld_file_content.splitlines()
    minemeld_list = sorted(set(minemeld_list))
    if minemeld_list == sorted(set(ip_list)):
        send_wr_log("File did not change! Exiting without processing.")
        sys.exit(-1)

    with open(filename, "w") as f:
        f.write(ip_addrs)

    ips_with_comma = ",".join(ip_list)
    ips_with_comma = ips_with_comma.rstrip(",")
    return ips_with_comma


def create_meraki_post_json(ip_list, comment):
    base_json = "{{\"protocol\":\"Any\", \"srcPort\":\"Any\", \"srcCidr\":\"Any\", \"destPort\":\"Any\", " \
                "\"destCidr\":\"{}\", \"policy\":\"allow\", \"syslogEnabled\":false, \"comment\":\"{}\"}}\n".format(ip_list, comment)
    return base_json


def main():
    ip_list = get_azure_minemeld()
    comment = COMMENT
    filename = "meraki_azure_json.txt"
    os.chdir(MAIN_DIR)
    if ip_list:
        meraki_azure_json = create_meraki_post_json(ip_list, comment)
        with open(filename, "w") as f:
            f.write(meraki_azure_json)
        send_wr_log("IP list is updated and json file for meraki is created!")

        # save historically
        historical_filename = MAIN_DIR + "/json_history/meraki_azure_json_" + str(int(time.time()))
        os.makedirs(os.path.dirname(historical_filename), exist_ok=True)
        with open(historical_filename, "w") as f:
            f.write(meraki_azure_json)
        send_wr_log("Json file for meraki is created!")

    else:
        send_wr_log("Error while getting ip list! IP list is empty.")
        sys.exit(-1)


if __name__ == '__main__':
    main()
