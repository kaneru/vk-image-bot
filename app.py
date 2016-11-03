#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import urllib2
import requests
import vk_auth
import os
import shutil
import random
import glob
from urllib import urlencode
from ConfigParser import SafeConfigParser

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

parser = SafeConfigParser()
parser.read("config.cfg")

email = parser.get('config', 'email')
password = parser.get('config', 'password')
client_id = parser.get('config', 'client_id')
token = vk_auth.auth(email, password, client_id, "photos,wall")[0]

folder = "images_to_post/"
images = glob.glob(folder + "*")
image_to_post = images[random.randint(0, len(images)) - 1]
img = {'photo': (image_to_post, open(image_to_post, 'rb'))}

def call_api(method, params, token):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params))
    return json.loads(urllib2.urlopen(url).read())["response"]

def upload_image(gid, token):
    us = call_api("photos.getWallUploadServer", [("group_id", gid)], token)
    upload_url = us["upload_url"]
    response = requests.post(upload_url, files=img)
    result = json.loads(response.text)
    image_id = call_api("photos.saveWallPhoto", [("group_id", gid), ("photo", result["photo"]), ("hash", result["hash"]), ("server", result["server"])], token)[0]["id"]
    return call_api("wall.post", [("owner_id", "-" + gid), ("attachments", image_id), ("message", "")], token)

upload_image("100558769", token)
shutil.copy(image_to_post, "posted_images/")
os.remove(image_to_post)