import ast
import math
import os
import urllib.parse
from datetime import datetime
import sys

import pymongo
from azure.storage.queue import QueueClient
from bson import ObjectId
from os.path import dirname as up

from .create_projects import add_to_projects_queue
from ..dump_projects.dump_results_of_a_project import get_entries_project

three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)


# from Simplified_System.end_to_end.create_projects import add_to_projects_queue

def refer_projects_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient("mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["projects"]  # creates a collection
    return mycol

def refer_collection():
  # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  myclient = pymongo.MongoClient("mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
  # mydb = myclient["CompanyDatabase"]  # creates a database
  mydb = myclient["miner"]  # creates a database
  mycol = mydb["comp_data_cleaned"]  # creates a collection
  return mycol

def create_and_queue_project(project_name,key_phrases,id):
    mycol = refer_projects_col()
    started_time = datetime.now()
    project_dict = {'project_name':project_name,'key_phrases':key_phrases,'created_time':started_time,'state':'queued','d_id':id}
    record_entry = mycol.insert_one(project_dict)
    print("Project stored in db: ", record_entry.inserted_id)
    print("Adding to projects queue")
    add_to_projects_queue([record_entry.inserted_id])

def check_ignore_flag(id_list):
    mycol = refer_collection()
    zeros =[]
    ones = []
    other = []
    filtered_list = []
    ignored_links = []
    for id_a in id_list:
        entry = mycol.find({"_id": id_a})
        data = [d for d in entry]
        if('ignore_flag' in data[0].keys()):
            if(data[0]['ignore_flag']=='0'):
                # filtered_list.append(id_a)
                zeros.append(id_a)
            elif(data[0]['ignore_flag']=='1'):
                ones.append(id_a)
            else:
                other.append(id_a)

            # print("yes",data[0]['ignore_flag'])
            # if(data[0]['ignore_flag']=='1'):
            #     ignored_links.append(data[0]['link'])
            #     # print('ignored',id_a)
            #     id_list.remove(id_a)
            # else:
            #     print([id_a,data[0]['ignore_flag'],data[0]['link']])

        else:
            print([id_a,data[0]['link']])
    # print(ignored_links)
    print('ig',len(ignored_links))
    print('ones',len(ones))
    print('zeros',len(zeros))
    print('other',len(other))
    # for k in ones:
    #     id_list.remove(k)

    print('filtered',len(id_list))

    return zeros

def get_project_state(id):
    mycol = refer_projects_col()
    project_entry = mycol.find({"d_id": id})
    data = [i for i in project_entry]
    print("kk",data)
    return data[-1]['state']

def get_completion_state(id):
    print("project_id",id)
    mycol = refer_projects_col()
    profiles_col = refer_collection()
    project_entry = mycol.find({"d_id": id})
    data = [i for i in project_entry]
    associated_entries = list(set(get_entries_project(id)))

    print('asso',len(associated_entries))
    associated_entries = check_ignore_flag(associated_entries)
    print('flag', len(associated_entries))
    completed_count = 0
    for each_entry in associated_entries:
        profile = profiles_col.find({"_id": each_entry})
        pr_data = [i for i in profile]
        if('simplified_dump_s_c_state' in pr_data[0].keys()):
            if(pr_data[0]['simplified_dump_s_c_state']=='Completed'):
                # print(each_entry,pr_data[0]['simplified_dump_state'])
                completed_count+=1
            # else:
            #     print('ddddd',pr_data[0]['simplified_dump_s_c_state'],each_entry)

    print('completed_count',completed_count)
    if(len(associated_entries)):
        completion_percentage = round((completed_count/len(associated_entries)*100),2)
        completion_count = str(completed_count)+" out of "+str(len(associated_entries))
        print(completion_percentage)
    else:
        completion_percentage = 0.0
        completion_count = "0 out of 0"
    return [completion_percentage,completion_count]
# create_and_queue_project('Test softwares project',['school management', 'educational software'],'1234')