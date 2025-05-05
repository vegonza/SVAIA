import re
import requests

url = 'https://www.uma.es/'
response = requests.get(url)
html = response.text

# Expresi´on regular para encontrar etiquetas <img>
subdomains = re.findall(r'([a-zA-Z0-9-]+)\.uma\.es', html)
subdomains = sorted(set(subdomains))
subdomains = [f"https://{subdomain}.uma.es" for subdomain in subdomains]

print("Subdominios encontrados:")
for subdomain in subdomains:
    print(subdomain)
