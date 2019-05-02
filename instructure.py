#!/usr/bin/env python3

import json
import urllib.request
import configparser
import functools
from joblib import Memory
memory = Memory('.',verbose=0)

config=configparser.ConfigParser()
config.read('config.conf')
token=config['DEFAULT']['token']
school=config['DEFAULT']['school']

@memory.cache
def get_json(query):
    baseurl='https://'+school+'.instructure.com/api/v1/'
    opener=urllib.request.build_opener()
    opener.addheaders=[('Authorization','Bearer '+token)]
    urllib.request.install_opener(opener)
    resp=urllib.request.urlopen(baseurl+query)
    return json.load(resp)

def get_courses():
    query="courses"
    data=get_json(query)
    return data

def get_assignments(course):
    query = 'courses/'+str(course)+'/assignment_groups?include[]=submission&per_page=40&include[]=assignments'
    data=get_json(query)
    return data

def print_grades(course):
    data=get_assignments(course)
    total=0
    for group in data:
        ptotal=0
        tscore=0
        weight=group['group_weight']
        for assign in group['assignments']:
            score=assign['submission']['score']
            pscore=assign['points_possible']
            if type(score)!=type(weight):
                score=0
            if type(pscore)!=type(weight):
                pscore=0
            ptotal+=pscore
            tscore+=score
            print(" "+str(score).ljust(8)+assign['name'])
        total+=(tscore/ptotal)*weight
    print(" {:.2f}".format(total))

courses=get_courses()
for course in courses:
    print(course['name'])
    print_grades(course['id'])

