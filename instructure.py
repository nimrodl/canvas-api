#!/usr/bin/env python3

import json
import urllib.request
import configparser
import html2text
import re
import datetime
from joblib import Memory
memory = Memory('.',verbose=0)

class school:
        config=configparser.ConfigParser()
        config.read('config.conf')
        token=config['DEFAULT']['token']
        school=config['DEFAULT']['school']

@memory.cache
def get_json_cache(req):
    resp=urllib.request.urlopen(req)
    return json.load(resp)

def get_json(query,cache=True):
    conf=school()
    url='https://'+conf.school+'.instructure.com/api/v1/'+query
    req=urllib.request.Request(url)
    req.add_header('Authorization','Bearer '+conf.token)
    if cache:
        return get_json_cache(req)
    else:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)

class instructure:

    def __init__(self):
        self.courses={}
        for course in get_json("courses",False):
            if not re.match(r"^ORI.*",course['name']):
                end=datetime.datetime.strptime(course['end_at'], "%Y-%m-%dT%H:%M:%SZ") + datetime.timedelta(days=7)
                self.courses[course['id']]={}
                self.courses[course['id']]['cache']=True
                if datetime.datetime.now()<end:
                    self.courses[course['id']]['cache']=False
                self.courses[course['id']]['course']=course
                self.courses[course['id']]['assignments']={}
                self.courses[course['id']]['discussions']={}

    def get_assignments(self,course):
        query = 'courses/'+str(course)+'/assignment_groups?include[]=submission&per_page=40&include[]=assignments'
        self.courses[course]['assignments']=get_json(query,self.courses[course]['cache'])

    def get_discussions(self,course):
        query = 'courses/'+str(course)+'/discussion_topics'
        for discussion in get_json(query,self.courses[course]['cache']):
            self.courses[course]['discussions'][discussion['id']]=discussion

    def get_view(self,course,discussion):
        query = 'courses/'+str(course)+'/discussion_topics/'+str(discussion)+'/view'
        data= get_json(query,self.courses[course]['cache'])
        self.courses[course]['discussions'][discussion]['view']={}
        self.courses[course]['discussions'][discussion]['participants']={}
        for post in data['view']:
            if post.get('user_id'):
                self.courses[course]['discussions'][discussion]['view'][post['id']]=post
        for part in data['participants']:
            self.courses[course]['discussions'][discussion]['participants'][part['id']]=part

    def print_grades(self,course):
        self.get_assignments(course)
        total=0
        for group in self.courses[course]['assignments']:
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

ins=instructure()
h=html2text.HTML2Text()
for id in ins.courses:
    print(ins.courses[id]['course']['name'])
    ins.print_grades(id)
    ins.get_discussions(id)
    for discussion in ins.courses[id]['discussions']:
        ins.get_view(id,discussion)
        for view in ins.courses[id]['discussions'][discussion]['view']:
            #print(ins.courses[id]['course']['name'])
            disc=ins.courses[id]['discussions'][discussion]
            #print(disc['title'])
            #print(disc['participants'][ disc['view'][view]['user_id'] ]['display_name'])
            #print(disc['view'][view]['created_at'])
            #print(h.handle(disc['view'][view]['message']))
            pass

