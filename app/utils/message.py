import os
import json

file = open(os.getcwd() + '/response_msg.json')
msg = json.load(file)