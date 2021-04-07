#!/usr/bin/env python3

import requests
import sys
import time
import os
from logger import send_wr_log


COMMENT = "office365_minemeld"
MAIN_DIR = '/nw/meraki/automation-scripts/update_meraki_rules'
IP_ADDR_LIST_URL ="https://10.62.0.155/feeds/o365-any-any-ipv4-feed?tr=1"
DOMAIN_LIST_URL = "https://10.62.0.155/feeds/o365-any-any-url-feed"
requests.packages.urllib3.disable_warnings()


def get_o365_minemeld():
    os.chdir(MAIN_DIR)
    try:
        response = requests.request(method="GET", url=IP_ADDR_LIST_URL, verify=False, timeout=15)
        if response.status_code != 200 or response.text == "":
            print("invalid response from minemeld")
            send_wr_log("Invalid response while getting IPv4 feed from minemeld! Code: {}".format(str(response.status_code)))
            sys.exit(-1)
        ip_addrs = response.text

        response = requests.request(method="GET", url=DOMAIN_LIST_URL, verify=False, timeout=15)
        if response.status_code != 200 or response.text == "":
            print("invalid response from minemeld")
            send_wr_log("Invalid response while getting URL feed from minemeld! Code: {}".format(str(response.status_code)))
            sys.exit(-1)
        domains = response.text
    except requests.exceptions.ConnectionError as e:
        send_wr_log("Connection Error: {}".format(str(e)))
        sys.exit(-1)
    except Exception as e:
        send_wr_log("Not handled exception: {}".format(str(e)))
        sys.exit(-1)

    ip_domain_str = ip_addrs + domains

    ip_list = ip_addrs.splitlines()
    initial_domain_list = domains.splitlines()
    # delete invalid urls
    domain_list = []
    for item in initial_domain_list:
        idx = item.find("*")
        if idx == 0:
            if item[1] != ".":
                send_wr_log("Invalid input for meraki firewall rule, removed: {}".format(item))
                continue
        idx = item.find("*", 1)
        if idx != -1:
            send_wr_log("Invalid input for meraki firewall rule, removed: {}".format(item))
            continue
        domain_list.append(item)

    ip_domain_list = ip_list + domain_list

    filename = "o365_minemeld.txt"
    with open(filename, "r") as f:
        minemeld_file_content = f.read()

    minemeld_list = minemeld_file_content.splitlines()
    minemeld_list = sorted(set(minemeld_list))
    if minemeld_list == sorted(set(ip_domain_list)):
        print("ALREADY UP TO DATE!")
        send_wr_log("File {} did not change! Exiting without processing.".format(filename))
        sys.exit(-1)

    with open(filename, "w") as f:
        f.write(ip_domain_str)
    ips_domains_with_comma = ",".join(ip_domain_list)
    ips_domains_with_comma = ips_domains_with_comma.rstrip(",")
    return ips_domains_with_comma


def create_meraki_post_json(ip_domain_list, comment):
    base_json = "{{\"protocol\":\"Any\", \"srcPort\":\"Any\", \"srcCidr\":\"Any\", \"destPort\":\"Any\", " \
                "\"destCidr\":\"{}\", \"policy\":\"allow\", \"syslogEnabled\":false, \"comment\":\"{}\"}}\n".format(ip_domain_list, comment)
    return base_json


def main():
    ip_list = get_o365_minemeld()
    comment = COMMENT
    filename = "meraki_o365_json.txt"
    os.chdir(MAIN_DIR)
    if ip_list:
        meraki_o365_json = create_meraki_post_json(ip_list, comment)
        with open(filename, "w") as f:
            f.write(meraki_o365_json)
        send_wr_log("IP list is updated and json file {} is written!".format(filename))
        historical_filename = MAIN_DIR + "/json_history/meraki_o365_json_" + str(int(time.time()))
        os.makedirs(os.path.dirname(historical_filename), exist_ok=True)
        with open(historical_filename, "w") as f:
            f.write(meraki_o365_json)
        print("UPDATED!")
    else:
        print("ERROR!")
        send_wr_log("Error while getting ip list! IP list is empty.")
        sys.exit(-1)


if __name__ == '__main__':
    main()
