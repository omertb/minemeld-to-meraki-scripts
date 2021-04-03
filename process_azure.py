#!/usr/bin/env python3
import requests
import sys
import time
import os

COMMENT = "azure_westeurope_minemeld"
AZURE_WEST_URL = "https://10.62.0.155/feeds/D365AzureIPRangeOutput"
requests.packages.urllib3.disable_warnings()


def get_azure_minemeld():
    os.chdir('/nw/meraki/automation-scripts/update_meraki_rules')
    response = requests.request(method="GET", url=AZURE_WEST_URL, verify=False)

    if response.status_code != 200 or response.text == "":
        print("minemeld\'den gecersiz cevap döndü")
        sys.exit(-1)
        return None
    ip_addrs = response.text

    all_ip_list = ip_addrs.splitlines()
    ip_list = [ip for ip in all_ip_list if not ":" in ip]
    ip_addrs = "\n".join(ip_list)

    filename = "azure_westeurope_minemeld.txt"
    with open(filename, "r") as f:
        minemeld_file_content = f.read()
        minemeld_list = minemeld_file_content.splitlines()
        minemeld_list = sorted(set(minemeld_list))
        if minemeld_list == sorted(set(ip_list)):
            print("GUNCEL!")
            sys.exit(-1)
            return None

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
    os.chdir('/nw/meraki/automation-scripts/update_meraki_rules')
    if ip_list:
        meraki_azure_json = create_meraki_post_json(ip_list, comment)
        with open(filename, "w") as f:
            f.write(meraki_azure_json)
        historical_filename = "o365_azure_json_" + str(int(time.time()))
        with open(historical_filename, "w") as f:
            f.write(meraki_azure_json)
        print("GUNCELLENDI!")
    else:
        print("bir hata olustu!")
        sys.exit(-1)


if __name__ == '__main__':
    main()
