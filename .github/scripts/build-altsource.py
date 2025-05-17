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
base = {}
baseapp = {}
news = {}

with open("altsource/base.json", "r") as f:
    base = json.load(f)
with open("altsource/baseapp.json", "r") as f:
    baseapp = json.load(f)
with open("altsource/news.json", "r") as f:
    news = json.load(f)

base["apps"] = []
baseapp["versions"] = []

main = copy.deepcopy(base)
pre = copy.deepcopy(base)
mainapp = copy.deepcopy(baseapp)
preapp = copy.deepcopy(baseapp)
main["apps"].append(mainapp)
pre["apps"].append(preapp)

preapp["name"] = "Geode (Pre-Release)"

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

firstrel = True
firstprerel = True

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
        if firstrel:
            firstrel = False
            mainapp["appPermissions"]["entitlements"] = list(entitlements)
            mainapp["appPermissions"]["privacy"] = privacy
        if firstprerel:
            firstprerel = False
            preapp["appPermissions"]["entitlements"] = list(entitlements)
            preapp["appPermissions"]["privacy"] = privacy
        
    ver = {}
    ver["version"] = release["tag_name"]

main["news"] = [post for post in news["news"] if "onlyPreRelease" not in post or post["onlyPreRelease"] != True]
pre["news"] = copy.deepcopy(news["news"])
for d in pre["news"]:
    if "onlyPreRelease" in d:
        d.pop("onlyPreRelease")




with open(altsourcefolder / "main.json", "w") as f:
    f.write(json.dumps(main, indent=4))
with open(altsourcefolder / "pre.json", "w") as f:
    f.write(json.dumps(pre, indent=4))
