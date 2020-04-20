#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 15:38:25 2020

@author: alfred
"""


from flask import Flask, render_template, request, url_for, jsonify
app = Flask(__name__)

@app.route('/')
def index():
	return request.url
# class index(Resource):
#     def get(self):
#         return request.url

@app.route('/tests/endpoint', methods=['POST'])
def my_test_endpoint():
    input_json = request.get_json(force=True) 
    # force=True, above, is necessary if another developer 
    # forgot to set the MIME type to 'application/json'
    print (f'data from client:{input_json}')
    dictToReturn = {'answer':42}
    return jsonify(dictToReturn)

if __name__ == '__main__':
    app.run(debug=True)