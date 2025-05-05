import requests
import re

with open('subdomains/scripts.txt', 'r') as file:
    scripts = file.readlines()


def format_version_name(name, version):
    return f"{name}: v{version}"


regex_list = [
    r'version="([^"]+)"',
    r'v([0-9]+\.[0-9]+\.[0-9]+)',
    r'([0-9]+\.[0-9]+\.[0-9]+)',
]

versions_list = []
for script in scripts:
    script_name = script.split('/')[-1].strip()
    if script_name != "bootstrap.min.js":
        continue
    try:
        version = re.findall(r'([0-9]+\.[0-9]+\.[0-9]+)', script_name)
        if version:
            script_version = format_version_name(script_name, version[0])
            versions_list.append(script_version)
            continue

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        print(script)
        response = requests.get(script, headers=headers)
        js_script = response.text
        print(js_script)
        for regex in regex_list:
            version = re.findall(regex, js_script, re.MULTILINE)
            if version:
                print(f"for script {script_name} found version {version[0]} with regex {regex}")
                script_version = format_version_name(script_name, version[0])
                versions_list.append(script_version)
                continue

    except Exception as e:
        print(f'{script}: {e}')

print(versions_list)
with open('subdomains/versiones.txt', 'w') as file:
    for version in versions_list:
        file.write(version + '\n')
