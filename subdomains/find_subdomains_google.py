import os
import sys
import time

import requests
from dotenv import find_dotenv, load_dotenv

from subdominios import main as search_subdomains_from_file

load_dotenv(find_dotenv())

API_KEY = os.environ.get("API_KEY")
CSE_ID = os.environ.get("CSE_ID")


def build_query(domain, excluded_subdomains):
    exclusions = ' '.join(f'-{sub}.{domain}' for sub in excluded_subdomains)
    return f"site:*.{domain} -www.{domain} {exclusions}"


def search_subdomains(domain, pages):
    start_index = 1
    subdomains = set()
    excluded_subdomains = set()
    base_url = f"https://www.googleapis.com/customsearch/v1"

    for _ in range(pages):
        print(f"processing page {_ + 1} of {pages}")
        query = build_query(domain, excluded_subdomains)
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

    print(f"found {len(subdomains)} subdomains, now looking into the html")
    for subdomain in sorted(subdomains):
        print(f"searching subdomains for {subdomain}")
        try:
            found = search_subdomains_from_file(f"https://{subdomain}")
            subdomains.update(found)
        except Exception as e:
            print(f"error: {e}")

    return subdomains


def main():
    domain = sys.argv[1]
    pages = int(sys.argv[2])

    subdomains = search_subdomains(domain, pages)
    with open('subdomains/google/subdominios.txt', 'w') as file:
        for subdomain in subdomains:
            file.write(subdomain + '\n')


if __name__ == "__main__":
    main()
