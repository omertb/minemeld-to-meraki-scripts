import requests
import json

requests.packages.urllib3.disable_warnings()
AZURE_JSON = "https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20210329.json"

def get_azure_json():
    response = requests.request(method="GET", url=AZURE_JSON, verify=False)
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
    print(ip_list)
    with open(filename, "w") as f:
        f.write(ip_list)


if __name__ == "__main__":
    main()