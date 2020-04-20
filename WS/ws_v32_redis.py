# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 12:54:24 2020

@author: James Ang
"""

from flask import Flask,request,jsonify

import redis
from rq import Queue
from ws_back import background_task

app = Flask(__name__)
r = redis.Redis() # create redis client using default 6379
q = Queue(connection=r)

@app.route('/',methods=['POST'])

def index():
    sen_level = request.form['seniority_level']
    return str(type(sen_level.split()))

@app.route('/scrape', methods=['POST'])

def scrape():
    # searched_word='PP Woven'
    # job_fcn='Purchasing'
    # sen_level='VP director manager senior'.split()
    searched_word = request.form['search_word']
    job_fcn = request.form['job_function']
    sen_level = request.form['seniority_level'].split()

    url1 = "http://www.indiaplasticdirectory.com/premium.asp?id=166&catid=4"
    # url2 = "https://www.alibaba.com/"
    url3 = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
    
    job = q.enqueue(background_task, url1,searched_word,url3,job_fcn,sen_level)
        
    # return f" Task {job.id} added to queue at {job.enqueued_at}. tasks in the queue."
    return f"Scraping has started. It will take a several minutes. Results will be returned when ready."    

if __name__ == '__main__':
    app.run(debug=True)