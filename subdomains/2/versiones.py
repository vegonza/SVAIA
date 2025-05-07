import re

from requests.sessions import Session

with open('scripts.txt', 'r') as file:
    scripts = file.readlines()


def format_version_name(name, version):
    return f"{name}: v{version}"


regex_list = [
    r'version="([^"]+)"',
    r'v([0-9]+\.[0-9]+\.[0-9]+)',
    r'([0-9]+\.[0-9]+\.[0-9]+)',
]

session = Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.uma.es/',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
}
session.get('https://www.uma.es/', headers=headers)

versions_list = []
for script in scripts:
    script = script.strip()
    script_name = script.split('/')[-1].strip()
    try:
        version = re.findall(r'([0-9]+\.[0-9]+\.[0-9]+)', script_name)
        if version:
            script_version = format_version_name(script_name, version[0])
            versions_list.append(script_version)
            continue

        # fake headers
        response = session.get(script, headers=headers, allow_redirects=True)
        if response.status_code != 200:
            continue

        js_script = response.text

        for regex in regex_list:
            version = re.findall(regex, js_script, re.MULTILINE)
            if version:
                print(f"for script {script_name} found version {version[0]} with regex {regex}")
                script_version = format_version_name(script_name, version[0])
                versions_list.append(script_version)
                break

    except Exception as e:
        print(f'{script}: {e}')

print(versions_list)
with open('versiones.txt', 'w') as file:
    for version in versions_list:
        file.write(version + '\n')
