import requests
import json
import os
import sys
from pathlib import Path
import plistlib
import copy

# Constants
temp_output = Path(os.getenv('OUTPUT'))
altsourcefolder = temp_output / "altsource"
altsourcefolder.mkdir(parents=True, exist_ok=True)
base = {}
news = {}


baseapp = {
    "name": "Geode Launcher",
    "bundleIdentifier": "com.geode.launcher",
    "developerName": "Geode SDK Team",
    "subtitle": "Geode, now on iOS!",
    "localizedDescription": "Geode, has come to iOS!",
    "iconURL": "https://raw.githubusercontent.com/geode-sdk/ios-launcher/main/Resources/Icons/Default.png",
    "tintColor": "#272727",
    "category": "games",
    "screenshots": [
        {
            "imageURL": "https://ios-repo.geode-sdk.org/img/LauncherShotiPhone-1.png",
            "width": 1242,
            "height": 2208
        },
        {
            "imageURL": "https://ios-repo.geode-sdk.org/img/LauncherShotiPhone-2.png",
            "width": 2208,
            "height": 1242
        },
        {
            "imageURL": "https://ios-repo.geode-sdk.org/img/LauncherShotiPhone-3.png",
            "width": 2208,
            "height": 1242
        }
    ],
    "versions": [],
    "appPermissions": {}
}

with open("altsource/base.json", "r") as f:
    base = json.load(f)
with open("altsource/news.json", "r") as f:
    news = json.load(f)


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
    headers['User-Agent'] = os.getenv('REPO_OWNER')
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
        
    makefile = requests.get(f"https://raw.githubusercontent.com/geode-sdk/ios-launcher/refs/tags/{release['tag_name']}/Makefile").text
    ver = {}
    ver["minOSVersion"] = makefile.split("\nTARGET := ")[1].split("\n")[0].split(":")[3]
    ver["version"] = release["tag_name"].split("v")[1]
    ver["localizedDescription"] = release["body"]
    ver["date"] = release["published_at"]
    for asset in release["assets"]:
        if asset["name"].endswith(".ipa"):
            ver["downloadURL"] = asset["browser_download_url"]
            ver["size"] = asset["size"]
    if not release["prerelease"]:
        mainapp["versions"].append(ver)
    preapp["versions"].append(ver)

main["news"] = [post for post in news["news"] if "onlyPreRelease" not in post or post["onlyPreRelease"] != True]
pre["news"] = copy.deepcopy(news["news"])
for d in pre["news"]:
    if "onlyPreRelease" in d:
        d.pop("onlyPreRelease")

with open(altsourcefolder / "main.json", "w") as f:
    f.write(json.dumps(main, indent=4))
with open(altsourcefolder / "pre.json", "w") as f:
    f.write(json.dumps(pre, indent=4))
