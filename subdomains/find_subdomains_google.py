import requests
import time
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

API_KEY = os.environ.get("API_KEY")
CSE_ID = os.environ.get("CSE_ID")

domain = "uma.es"
query = f"site:*.{domain} -www.{domain}"
base_url = f"https://www.googleapis.com/customsearch/v1"

subdomains = set()
excluded_subdomains = set()
start_index = 1
max_pages = 1000


def build_query():
    exclusions = ' '.join(f'-{sub}.{domain}' for sub in excluded_subdomains)
    return f"site:*.{domain} -www.{domain} {exclusions}"


for page in range(max_pages):
    query = build_query()
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
        "start": start_index
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if "items" not in data:
        break

    new_found = False

    for item in data["items"]:
        link = item["link"]
        link = link.split("//")[-1].split("/")[0]
        if link.endswith(domain):
            if link not in subdomains:
                subdomains.add(link)
                sub_part = link.replace(f".{domain}", "")
                excluded_subdomains.add(sub_part)
                new_found = True

    start_index += 10

    if start_index > 100:
        # After every 100 results, reset start index and rebuild exclusions
        start_index = 1
        if not new_found:
            break

    time.sleep(1)

for subdomain in sorted(subdomains):
    print(subdomain)
