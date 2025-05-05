import re

import requests

url = 'https://www.uma.es/'
response = requests.get(url)
html = response.text

subdomains = re.findall(r'([a-zA-Z0-9-]+)\.uma\.es', html)
subdomains = sorted(set(subdomains))
subdomains = [f"https://{subdomain}.uma.es" for subdomain in subdomains]

with open('subdomains/subdominios.txt', 'w') as file:
    for subdomain in subdomains:
        file.write(subdomain + '\n')
