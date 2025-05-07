import re

import requests

url = 'https://www.uma.es'
response = requests.get(url)
html = response.text

scripts = re.findall(r'src="([^"]+\.js)"', html)
scripts = sorted(set(scripts))
scripts = [f"{url}{script}" if "https://" not in script else script for script in scripts]

with open('scripts.txt', 'w') as file:
    for script in scripts:
        file.write(script + '\n')
