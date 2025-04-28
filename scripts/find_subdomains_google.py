import os
from dotenv import find_dotenv, load_dotenv

from googleapiclient.discovery import build
from urllib.parse import urlparse

load_dotenv(find_dotenv())

api_key = os.environ.get("API_KEY")
cse_id = os.environ.get("CSE_ID")

def get_subdomains_api(url, api_key, cse_id):
    service = build("customsearch", "v1", developerKey=api_key)
    query = f"site:{url} -inurl:www"
    
    try:
        result = service.cse().list(q=query, cx=cse_id).execute()
        subdomains = set()
        
        if "items" in result:
            for item in result["items"]:
                link = item.get("link")
                parsed_url = urlparse(link)
                subdomain = parsed_url.netloc
                if subdomain and subdomain != url:
                    subdomains.add(subdomain)
        
        return list(subdomains)
    
    except Exception as e:
        print(f"Error en la API: {e}")
        return []

if __name__ == "__main__":
    url = input("Ingrese la URL: ")
    subdomains = get_subdomains_api(url, api_key, cse_id)
    print("Subdominios encontrados:", subdomains)