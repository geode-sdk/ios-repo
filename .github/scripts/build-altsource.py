import requests
import json
import hashlib
import os
import sys
import zipfile
from pathlib import Path
import subprocess
import plistlib
import copy

# Constants
temp_output = Path(os.getenv('OUTPUT'))
altsourcefolder = temp_output / "altsource"
altsourcefolder.mkdir(parents=True, exist_ok=True)
base = json.load("altsource/base.json")
baseapp = json.load("altsource/baseapp.json")
news = json.load("altsource/news.json")

base["apps"] = []
baseapp["versions"] = []

main = copy.deepcopy(base)
pre = copy.deepcopy(base)
mainapp = copy.deepcopy(baseapp)
preapp = copy.deepcopy(baseapp)
main["apps"].append(mainapp)
pre["apps"].append(preapp)

# Functions
def send_authenticated_request(url, headers=None):
    if headers is None:
        headers = {}
    headers['Authorization'] = f'Bearer {os.getenv("gh_token")}'
    headers['User-Agent'] = 'coopeeo' # Change this later
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response

# Main
releases = send_authenticated_request("https://api.github.com/repos/geode-sdk/ios-launcher/releases").json()

firstrel = False
firstprerel = False

for release in releases:
    if firstprerel or firstrel:
        entitlements = []
        privacy = {}
        entitlementsplist = plistlib.loads(requests.get(f"https://raw.githubusercontent.com/geode-sdk/ios-launcher/refs/tags/{release['tag_name']}/entitlements.xml").content)
        privacyplist = plistlib.loads(requests.get(f"https://raw.githubusercontent.com/geode-sdk/ios-launcher/refs/tags/{release['tag_name']}/Resources/Info.plist").content)

        entitlements = entitlementsplist.keys()
        for privacykey in privacyplist:
            if (privacykey.endswith("UsageDescription")):
                privacy[privacykey] = privacyplist[privacykey]
        
    ver = {}
    ver["version"] = release["tag_name"]
