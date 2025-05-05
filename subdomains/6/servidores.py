import sys

import requests


def main():
    lista = sys.argv[1]
    with open(lista, 'r') as file:
        subdomains = file.readlines()

    web_servers = []
    for subdomain in subdomains:
        print(f"checking subdomain: {subdomain}")
        data = {}
        try:
            subdomain = subdomain.strip()
            name = f"https://{subdomain}"
            response = requests.get(name)

            data['name'] = name
            data['server'] = response.headers.get('Server', 'Unknown')
            data['powered_by'] = response.headers.get('X-Powered-By', 'Unknown')
            web_servers.append(data)
        except:
            print(f"error")

    with open('servidores.txt', 'w') as file:
        for data in web_servers:
            file.write(f"{data['name']}: Server: {data['server']} - Powered by: {data['powered_by']}\n")


if __name__ == "__main__":
    main()
