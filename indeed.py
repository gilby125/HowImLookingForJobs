#!/usr/bin/python3.5
# -*- coding:utf-8 -*-

###
### Author: Alan LE MOUROUX
### Date: 05/10/2016
###

import time
import sys
import signal
import sqlite3
import smtplib
import requests
import json
import asyncio
import websockets
from bs4 import BeautifulSoup

# Loads configuration
with open('config.json') as config_file:
    config = json.load(config_file)
#---/Loads configuration

# Builds search url
url = 'http://www.indeed.' + config['country']
try:
    r = requests.get(url + '/advanced_search')
except requests.exceptrions.RequestException as e:
    print(e)
    sys.exit(1)
page = r.text
soup = BeautifulSoup(page, 'lxml')
form = soup.find('form', {'name':'sf'})
loc = config['city']
loc += (',' + config['canton']) if config['canton'] != '' else ''
loc += (',' + config['postcode']) if config['postcode'] != '' else ''
params = {
    'as_and': '',
    'as_phr': '',
    'as_any': config['jobs'],
    'as_not': '',
    'as_ttl': '',
    'as_cmt': '',
    'jt': 'all',
    'st': '',
    'radius': config['radius'],
    'l': loc,
    'fromage': '1',
    'limit': '50',
    'sort': 'date',
    'psf': 'advsrch',
}
form_url = url + form['action'] + '?'
for name, val in params.items():
    if isinstance(val, list):
        val = '+'.join(val)
    form_url += ('&' + name + '=' + val)
#---/Builds search url

# Connects to the database and creates the job table if needed
conn = sqlite3.connect('indeed.db')
c = conn.cursor()
c.execute('SELECT * FROM sqlite_master WHERE name = \'jobs\'')
if c.fetchone() is None:
    c.execute('CREATE TABLE jobs ' +
              '(job_id INTEGER PRIMARY KEY, title TEXT, ' +
              'company TEXT, location TEXT, summary TEXT)')
    conn.commit()
#---/Connects to the database and creates the job table if needed

# Email parameters
user = config['email']
pwd = config['email_pwd']
email_srv = smtplib.SMTP(config['email_smtp'])
email_srv.ehlo()
email_srv.starttls()
email_srv.login(user, pwd)
#---/Email parameters

# Registers new job and sends a mail about it
def process_new_job(job):
    msg = "\r\n".join([
        "From: " + user,
        "To: " + user,
        "Subject: [IndeedScript][NewJobFound]",
        "",
        "New Job !!\n" +
        "------------------\n" +
        "date: " + job['date'] + "\n" +
        "title: " + job['title'] + "\n" +
        "company: " + job['company'] + "\n" +
        "location: " + job['location'] + "\n" +
        "summary: " + job['summary'] + "\n" +
        "link: " + url + job['link'] + "\n" +
        "------------------\n"
    ])
    email_srv.sendmail(user, user, msg.encode('utf-8'))
    c.execute('INSERT INTO jobs VALUES (NULL, ?, ?, ?, ?)', (
              job['title'],
              job['company'],
              job['location'],
              job['summary']))
#---/Registers new job and sends a mail about it

# Tests if job is new
def is_new(job):
    c.execute('SELECT job_id FROM jobs WHERE ' +
              'title = ? and ' +
              'company = ? and ' +
              'location = ? and ' +
              'summary = ?', (
                  job['title'],
                  job['company'],
                  job['location'],
                  job['summary']
              ))
    fetched = c.fetchone()
    if fetched is None:
        return True
    return False
#---/Tests if job is new

# Registers a ctrl-c handler which free resources before quitting
def sigint_handler(signal, frame):
    print("\nBye !")
    conn.close()
    email_srv.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)
#---/Registers a ctrl-c handler which free resources before quitting

# Scrapes the website every x seconds and notifies the user of new jobs
async def scrape_jobs(websocket, path):
    isReady = await websocket.recv()
    while isReady != 'ok':
        print("Wrong message from js interpreter:", isReady, " => \"ok\" expected")
        isReady = await websocket.recv()
    while True:
        await websocket.send(form_url)
        page = await websocket.recv()
        soup = BeautifulSoup(page, 'lxml')
        for result in soup.find_all('div', {'class': 'result'}):
            job = {
                'date': result.find(True, {'class': 'date'}),
                'title': result.find(True, {'class': 'jobtitle'}),
                'company': result.find(True, {'class': 'company'}),
                'location': result.find(True, {'class': 'location'}),
                'summary': result.find(True, {'class': 'summary'}),
                'link' : result.find(True, {'class': 'turnstileLink'})['href'],
            }
            for name, val in job.items():
                if name != "link":
                    if val is None:
                        job[name] = "N/A"
                    else:
                        job[name] = val.get_text()
            if job['date'] == 'Today' and is_new(job):
                print("New Job Added")
                process_new_job(job)
        conn.commit()
        time.sleep(config['delay'])

start_server = websockets.serve(scrape_jobs, 'localhost', 8002)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
#---/Scrapes the website every x seconds and notifies the user of new jobs
