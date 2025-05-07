import re

import requests


def main(url):
    response = requests.get(url)
    html = response.text

    subdomains = re.findall(r'([a-zA-Z0-9-]+)\.uma\.es', html)
    subdomains = sorted(set(subdomains))
    subdomains = [f"{subdomain}.uma.es" for subdomain in subdomains]

    return subdomains


if __name__ == "__main__":
    url = 'https://www.uma.es/'
    subdomains = main(url)

    with open('subdominios.txt', 'w') as file:
        for subdomain in subdomains:
            file.write(subdomain + '\n')
