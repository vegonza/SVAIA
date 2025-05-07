import re

import requests

url = 'https://www.uma.es/'
response = requests.get(url)
html = response.text

links = re.findall(r'href="([^"]+)"', html)
links = sorted(set(links))
links = [f"{url}{link}" if "https://" not in link else link for link in links]

with open('enlaces.txt', 'w') as file:
    for link in links:
        file.write(link + '\n')
