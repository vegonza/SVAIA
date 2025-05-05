import sys

import requests


def verify_subdomains(domain, lista):
    with open(lista, 'r') as file:
        subdomains = file.readlines()

    for subdomain in subdomains:
        subdomain = subdomain.strip()
        print(f"checking subdomain: https://{subdomain}.{domain}")
        try:
            requests.get(f"https://{subdomain}.{domain}")
            print(f"{subdomain}.{domain} is valid")
        except:
            print(f"{subdomain}.{domain} is not valid")

    with open('subdominios.txt', 'w') as file:
        for subdomain in subdomains:
            file.write(subdomain + '\n')


def main():
    domain = sys.argv[1]
    lista = sys.argv[2]

    verify_subdomains(domain, lista)


if __name__ == "__main__":
    main()
