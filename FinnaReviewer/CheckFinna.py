#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2020 Michael Daniels
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
import time
import re
import json
from PIL import Image

S = requests.Session()
# Comment out the first or second idURLString and regexID.

#idURLString = 'https:\/\/(www\.)?finna\.fi\/Record\/.{3}\..{10}:.{8}'
#idURLString = 'https:\/\/www\.finna\.fi\/Record\/musketti\..{4}:.{10}:.{3}'
idURLString = 'https:\/\/(?:www\.)?finna\.fi\/Record\/(?:hkm\.|musketti\..{4}:)'
idURLString = idURLString + '.{6,10}:(?:[^"]{8}|[^"]{3})'
regexIDURL = re.compile(idURLString, re.IGNORECASE)

#regexID = re.compile('.{3}\..{10}:.{8}', re.IGNORECASE)
#regexID = re.compile('musketti\..{4}:.{10}:.{3}', re.IGNORECASE)
regexID = re.compile('(?:hkm\.|musketti\..{4}:).{4,10}:(?:[^"]{8}|[^"]{3})',
    re.IGNORECASE)

regexCCBY40 = re.compile('{{cc[- ]by[- ]4\.0}}', re.IGNORECASE)
outFilePass = open("outFilePass.txt", 'a')
outFileFail = open("outFileFail.txt", 'a')

myUserAgentA = "Finna License Checker, Wikimedia Commons. "
myUserAgentB = "Contact: en.wikipedia.org/wiki/User:Mdaniels5757 "
myUserAgentC = "& click 'email this user'"
headers = {
    'User-Agent': str(myUserAgentA + myUserAgentB + myUserAgentC)
}

def GetCopyrightData(id):
    URLBase = "https://api.finna.fi/api/v1/record?id="
    URL = URLBase + id + "&field[]=imageRights&prettyPrint=false&lng=en-gb"
    raw = requests.get(URL, headers=headers)
    if (not raw):
        print("Finna Data Error")
        return
    response = json.loads(raw.text)
    imageRights = response["records"][0]["imageRights"]
    copyright = imageRights["copyright"]
    return copyright
    
def downloadImages(line, id):
    # Get finna image: small if avail, master if not
    URLBase = "https://api.finna.fi/api/v1/record?id="
    URL = URLBase + id + "&field[]=imagesExtended&prettyPrint=false&lng=en-gb"
    raw = requests.get(URL, headers=headers)
    response = json.loads(raw.text)
    sizes = response["records"][0]["imagesExtended"][0]["urls"]
    finnaURLBase = "https://www.finna.fi/Cover/Show?id="
    if "small" in sizes:
        finnaURLBase = "https://www.finna.fi/Cover/Show?id="
        finnaURL = finnaURLBase + id + "&index=0&size=small"
    else:
        finnaURL = finnaURLBase + id + "&index=0&size=master"
    finnaFile = open('finnaFile.jpg', 'wb')
    finnaFile.write(requests.get(finnaURL, headers=headers).content)
    finnaFile.close()
    with Image.open('finnaFile.jpg') as img:
        width, height = img.size
        finnaSize = width, height
        print(str(width) + ", " + str(height))
    
    # Set up Commons API again to get image url
    URL = "https://commons.wikimedia.org/w/api.php"
    params = {
    	"action": "query",
    	"format": "json",
    	"prop": "imageinfo",
        "indexpageids": 1,
    	"titles": line,
        "maxlag": "5",
    	"iiprop": "url",
        "iiurlwidth": str(width),
        "iiurlheight": str(height)
    }
    raw = S.get(url=URL, params=params, headers=headers)
    response = raw.json()
    pageID = response["query"]["pageids"][0]
    commonsURL = response["query"]["pages"][pageID]["imageinfo"][0]["thumburl"]
    commonsFile = open('commonsFile.jpg', 'wb')
    commonsFile.write(requests.get(commonsURL, headers=headers).content)
    commonsFile.close()
    
def CompareImages():
    i1orig = Image.open("commonsFile.jpg")
    i1 = i1orig.convert("RGB")
    i2orig = Image.open("finnaFile.jpg")
    i2 = i2orig.convert("RGB")
    if i1.mode != i2.mode:
        print("Different kinds of images.")
        return 90
    if i1.size != i2.size:
        i1 = i1.resize(i2.size)
     
    pairs = zip(i1.getdata(), i2.getdata())
    if len(i1.getbands()) == 1:
        # for gray-scale jpegs
        dif = sum(abs(p1-p2) for p1,p2 in pairs)
    else:
        dif = sum(abs(c1-c2) for p1,p2 in pairs for c1,c2 in zip(p1,p2))
     
    ncomponents = i1.size[0] * i1.size[1] * 3
    # Return difference percentage
    return (dif / 255.0 * 100) / ncomponents

def perPage(line):
    # Set up API, find the ID
    URL = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "parse",
        "page": line,
        "maxlag": "5",
        "format": "json"
    }
    raw = S.get(url=URL, params=params, headers=headers)
    response = raw.json()
    wikicode = response["parse"]["text"]["*"]
    matchIDURL = regexIDURL.search(wikicode)
    if matchIDURL:
        # Find the ID and get copyright info
        matchURLstr = matchIDURL.group(0)
        print(matchURLstr)
        matchID = regexID.search(matchURLstr)
        finnaIDstr = matchID.group(0)
        print(finnaIDstr)
        copyright = GetCopyrightData(finnaIDstr)
    else:
        print("Regex no match")
        return
    if copyright != "CC BY 4.0":
        outFileFail.write(line)
        print("Failed - not CC-BY-4.0: " + line)
        return
    
    downloadImages(line, finnaIDstr)
    
    diffPercent = CompareImages()
    if diffPercent <= 9:
        outFilePass.write(line)
        str = "PASS: " + line + " diffPercent" + "{:.2f}".format(diffPercent)
    else:
        outFileFail.write(line)
        str = "Failed - different: " + line
        str = str + " diffPercent" + "{:.2f}".format(diffPercent)
    print(str)

with open("infile.txt",'r') as infile:
    for line in infile:
        perPage(line)
        time.sleep(1)
    outFilePass.close()
    outFileFail.close()
