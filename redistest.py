# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 21:59:11 2020

@author: User
"""
from flask import Flask, request
import redis
from rq import Queue

import time

app = Flask(__name__)

r = redis.Redis()
q = Queue(connection=r)

def background_task(n):
    
    delay = 2
    
    print('Task Running')
    print(f'Simulating {delay} second delay')
    
    time.sleep(delay)
    print(len(n))
    
    print('Task Complete')
    
    return len(n)


@app.route('/task')
def add_task():
    if request.args.get('n'):
        
        job = q.enqueue(background_task, request.args.get("n"))
        
        q_len = len(q)
        
        return f" Task {job.id} added to queue at {job.enqueued_at}. {q_len} tasks in the queue."
    
    return "No value for n"
    
if __name__ == "__main__":
    app.run()