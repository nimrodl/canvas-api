#!/usr/bin/env python3

import json
import urllib.request
import configparser
from joblib import Memory
memory = Memory('.',verbose=0)

class school:
        config=configparser.ConfigParser()
        config.read('config.conf')
        token=config['DEFAULT']['token']
        school=config['DEFAULT']['school']

@memory.cache
def get_json(query):
    conf=school()
    baseurl='https://'+conf.school+'.instructure.com/api/v1/'
    opener=urllib.request.build_opener()
    opener.addheaders=[('Authorization','Bearer '+conf.token)]
    urllib.request.install_opener(opener)
    resp=urllib.request.urlopen(baseurl+query)
    return json.load(resp)

class instructure:

    def __init__(self):
        self.courses={}
        for course in get_json("courses"):
            self.courses[course['id']]={}
            self.courses[course['id']]['course']=course
            self.courses[course['id']]['assignments']={}
            self.courses[course['id']]['discussions']={}

    def get_assignments(self,course):
        query = 'courses/'+str(course)+'/assignment_groups?include[]=submission&per_page=40&include[]=assignments'
        self.courses[course]['assignments']=get_json(query)

    def get_discussions(self,course):
        query = 'courses/'+str(course)+'/discussion_topics'
        for discussion in get_json(query):
            self.courses[course]['discussions'][discussion['id']]=discussion

    def get_view(self,course,discussion):
        query = 'courses/'+str(course)+'/discussion_topics/'+str(discussion)+'/view'
        data= get_json(query)
        for view in data:
            self.courses[course]['discussions'][discussion]['view']=data['view']

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
print(ins.courses.keys())
for id in ins.courses:
    print(ins.courses[id]['course']['name'])
    ins.print_grades(id)
    ins.get_discussions(id)
    for discussion in ins.courses[id]['discussions']:
        ins.get_view(id,discussion)
        for view in ins.courses[id]['discussions'][discussion]['view']:
            #print(view)
            pass

