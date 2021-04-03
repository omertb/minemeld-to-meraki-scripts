import requests
import sys
import time
import os

COMMENT = "office365_minemeld"
IP_ADDR_LIST_URL ="https://10.62.0.155/feeds/o365-any-any-ipv4-feed?tr=1"
DOMAIN_LIST_URL = "https://10.62.0.155/feeds/o365-any-any-url-feed"
requests.packages.urllib3.disable_warnings()


def get_o365_minemeld():
    os.chdir('/nw/meraki/automation-scripts/office365')
    response = requests.request(method="GET", url=IP_ADDR_LIST_URL, verify=False)

    if response.status_code != 200 or response.text == "":
        print("invalid response from minemeld")
        sys.exit(-1)
        return None
    ip_addrs = response.text

    response = requests.request(method="GET", url=DOMAIN_LIST_URL, verify=False)
    if response.status_code != 200 or response.text == "":
        print("invalid response from minemeld")
        sys.exit(-1)
        return None
    domains = response.text

    ip_domain_str = ip_addrs + domains

    ip_list = ip_addrs.splitlines()
    initial_domain_list = domains.splitlines()
    # delete invalid urls
    domain_list = []
    for item in initial_domain_list:
        idx = item.find("*")
        if idx == 0:
            if item[1] != ".":
                continue
        idx = item.find("*", 1)
        if idx != -1:
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
            sys.exit(-1)
            return None

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
    os.chdir('/nw/meraki/automation-scripts/office365')
    if ip_list:
        meraki_o365_json = create_meraki_post_json(ip_list, comment)
        with open(filename, "w") as f:
            f.write(meraki_o365_json)
        historical_filename = "o365_minemeld_json_" + str(int(time.time()))
        with open(historical_filename, "w") as f:
            f.write(meraki_o365_json)
        print("UPDATED!")
    else:
        print("ERROR!")
        sys.exit(-1)


if __name__ == '__main__':
    main()
