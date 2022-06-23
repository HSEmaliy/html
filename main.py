import json

import numpy as np
from jinja2 import Environment, FileSystemLoader
import plotly.express as px
import plotly.graph_objs as go
import requests as re
import os

root = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(root, 'template')
env = Environment(loader=FileSystemLoader(templates_dir))
template = env.get_template('index.html')
filename_index = os.path.join(root, 'index.html')
filename_emails = os.path.join(root, 'emails.txt')

my_email = 'avmaliy@miem.hse.ru'
my_ip = 'http://94.79.54.21:3000'
my_token = 'dIlUIIpKrjCcrmmM'
headers = {
    'Content-Type': 'application/json'
}
def get_statistics(ip, email, token):
    # ZULIP
    zulip_re = re.post(f'{ip}/api/zulip/getData', data=json.dumps({
        "studEmail": email,
        "beginDate": "2021-01-01",
        "endDate": "2023-01-01",
        "timeRange": 1,
        "token": token
    }), headers=headers)

    zulip_info = json.loads(zulip_re.content)
    channels = []
    zulip_count = 0
    try:
        zulip_count = len(zulip_info['messages'])
        for m in zulip_info['messages']:
            if m['name'] not in channels:
                channels.append(m['name'])
        channels = ', '.join(channels)
    except:
        pass
    # JITSI
    jitsi_re = re.post(f'{ip}/api/jitsi/sessions', data=json.dumps({
        "studEmail": email,
        "beginDate": "2021-01-01",
        "endDate": "2023-01-01",
        "token": token
    }), headers=headers)

    jitsi_info = json.loads(jitsi_re.content)
    rooms = []
    for l in jitsi_info:
        if l['room'] not in rooms:
            rooms.append(l['room'])
    rooms = ', '.join(rooms)

    jitsi_count = len(jitsi_info)

    # GIT
    git_re = re.post(f'{ip}/api/git/getData', data=json.dumps({
        "studEmail": email,
        "beginDate": "2021-01-01",
        "endDate": "2023-01-01",
        "timeRange": 1,
        "hideMerge": False,
        "token": token
    }), headers=headers)

    git_info = json.loads(git_re.content)

    git_count = 0
    try:
        for com in git_info['commits_stats']:
            git_count = git_count + com['commitCount']
    except:
        pass
    # TAIGA
    taiga_re = re.get('https://track.miem.hse.ru/api/v1/tasks')

    taiga_info = json.loads(taiga_re.content)

    taiga_count = 0

    actions = []

    for task in taiga_info:
        if task['assigned_to_extra_info']['username'] == email[:-12]:
            taiga_count = taiga_count + 1

    return [zulip_count, jitsi_count, git_count, taiga_count, channels, rooms]


emails = open(filename_emails, "r").read().split("\n")
zulip_avr = 0
jitsi_avr = 0
git_avr = 0
taiga_avr = 0

for e in emails:
    zulip_count, jitsi_count, git_count, taiga_count, channels, rooms = get_statistics(my_ip, e, my_token)
    zulip_avr = zulip_avr + zulip_count
    jitsi_avr = jitsi_avr + jitsi_count
    git_avr = git_avr + git_count
    taiga_avr = taiga_avr + taiga_count

zulip_avr = zulip_avr / len(emails)
jitsi_avr = jitsi_avr / len(emails)
git_avr = git_avr / len(emails)
taiga_avr = taiga_avr / len(emails)

zulip_count, jitsi_count, git_count, taiga_count, channels, rooms = get_statistics(my_ip, my_email, my_token)

# ZULIP
zulip_re = re.post(f'{my_ip}/api/zulip/getData', data=json.dumps({
    "studEmail": my_email,
    "beginDate": "2021-01-01",
    "endDate": "2023-01-01",
    "timeRange": 1,
    "token": my_token
}), headers=headers)

zulip_info = json.loads(zulip_re.content)

zulip_stat = {}
for m in zulip_info['messages']:
    if m['timestamp'][:10] not in list(zulip_stat.keys()):
        zulip_stat[m['timestamp'][:10]] = 1
    else:
        zulip_stat[m['timestamp'][:10]] = zulip_stat[m['timestamp'][:10]] + 1

# JITSI
jitsi_re = re.post(f'{my_ip}/api/jitsi/sessions', data=json.dumps({
    "studEmail": my_email,
    "beginDate": "2021-01-01",
    "endDate": "2023-01-01",
    "token": my_token
}), headers=headers)
jitsi_info = json.loads(jitsi_re.content)
jitsi_stat = {}
for l in jitsi_info:
    if l['date'] not in list(jitsi_stat.keys()):
        jitsi_stat[l['date']] = 1
    else:
        jitsi_stat[l['date']] = jitsi_stat[l['date']] + 1

timeline_zulip = go.Figure([go.Scatter(x=list(zulip_stat.keys()), y=list(zulip_stat.values()))])
timeline_jitsi = go.Figure([go.Scatter(x=list(jitsi_stat.keys()), y=list(jitsi_stat.values()))])

with open(filename_index, 'w') as fh:
    fh.write(template.render(my_zulip=zulip_count, my_jitsi=jitsi_count, my_git=git_count, my_taiga=taiga_count,
                             zulip_avr=zulip_avr, jitsi_avr=jitsi_avr, git_avr=git_avr, taiga_avr=taiga_avr,
                             channels=channels, rooms=rooms, timeline_zulip=timeline_zulip.to_html(),
                             timeline_jitsi=timeline_jitsi.to_html()))
