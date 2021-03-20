import ast
import os
import urllib.parse
from datetime import datetime
import sys

import pymongo
from azure.storage.queue import QueueClient
from bson import ObjectId
from os.path import dirname as up

from .power_thesaurus import get_results_pt

three_up = up(up(up(__file__)))
sys.path.insert(0, three_up)


# from Simplified_System.query_expansion.power_thesaurus import get_results_pt

def refer_collection():
  # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
  myclient = pymongo.MongoClient("mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
  # mydb = myclient["CompanyDatabase"]  # creates a database
  mydb = myclient["miner"]  # creates a database

  mycol = mydb["comp_data_cleaned"]  # creates a collection
  return mycol

def refer_projects_col():
    # myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    myclient = pymongo.MongoClient(
        "mongodb+srv://user_gihan:" + urllib.parse.quote("Gihan1@uom") + "@armitage.bw3vp.mongodb.net/test?retryWrites=true&w=majority")
    # mydb = myclient["CompanyDatabase"]  # creates a database
    mydb = myclient["miner"]  # creates a database
    mycol = mydb["projects"]  # creates a collection
    return mycol


def add_to_projects_queue(id_list):

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    connect_str = "DefaultEndpointsProtocol=https;AccountName=armitage;AccountKey=yUoQAb2ZRKKFiQBzMUTLKd1YSNbd0zjkgFaAz9OS9ze+RJW6DWbeeDsPmNfucyXlDEEGmU6WUlv36My2RARLLA==;EndpointSuffix=core.windows.net"
    projects_client = QueueClient.from_connection_string(connect_str, "projects-queue")
    for each_id in id_list:
        print(each_id," added to projects queue")
        projects_client.send_message([str(each_id)], time_to_live=-1)

def add_to_project_completion_queue(id_list):

    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    projects_client = QueueClient.from_connection_string(connect_str, "project-completion-queue")
    for each_id in id_list:
        print(each_id," added to projects completion queue")
        projects_client.send_message([str(each_id)], time_to_live=-1)

def add_to_initial_crawling_queue(name_list):
    mycol = refer_collection()
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    ic_client = QueueClient.from_connection_string(connect_str, "initial-crawling-queue")
    for name in name_list:
        print(name)
        ic_client.send_message([str(name)])

def process_queries(key_phrases):
    queries = []
    for each_phrase in key_phrases:
        # query = each_phrase+" in australia or newzealand"
        # queries.append(query)
        queries_from_pt = get_results_pt(each_phrase)
        for each_q in [each_phrase]+queries_from_pt[:5]:
            query = each_q+" in australia or newzealand"
            queries.append(query)

    return queries

def get_projects_via_queue():
    print("Projects queue is live")
    mycol = refer_projects_col()
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    projects_client = QueueClient.from_connection_string(connect_str, "projects-queue")
    while (True):
        rows = projects_client.receive_messages()
        for msg in rows:
            # time.sleep(60)
            row = msg.content
            row = ast.literal_eval(row)
            print(row[0],' processing queries from the key phrases')
            entry_id = ObjectId(row[0])
            proj_data_entry = mycol.find({"_id": entry_id})
            data = [i for i in proj_data_entry]
            print(data[0])
            key_phrases = data[0]['key_phrases']
            queries = process_queries(key_phrases)
            for each_query in queries:
                print(each_query," adding to pipeline execution")
                add_to_initial_crawling_queue([each_query+' ++'+str(entry_id)+' --project'])
            projects_client.delete_message(msg)
            add_to_project_completion_queue([entry_id])


            # try:
            #     comp_name = data[0]['comp_name']
            #     data_dict_aven = scrape_avention(comp_name)
            #     if (data_dict_aven == 'error'):
            #         print("Error has occured..retry")
            #     elif (len(data_dict_aven.keys())):
            #         mycol.update_one({'_id': entry_id},
            #                          {'$set': data_dict_aven})
            #         print("Successfully extended the data entry with avention profile information", entry_id)
            #         avention_client.delete_message(msg)
            #         mycol.update_one({'_id': entry_id},
            #                          {'$set': {'avention_extraction_state': 'Completed'}})
            #     else:
            #         print("No avention profile found! dict is empty")
            #         avention_client.delete_message(msg)
            #         mycol.update_one({'_id': entry_id},
            #                          {'$set': {'avention_extraction_state': 'Completed'}})
            #
            # except IndexError:
            #     print("Indexing error occured!")
            # except KeyError:
            #     print("Key error occured!")

def create_and_queue_project(project_name,key_phrases):
    mycol = refer_projects_col()
    started_time = datetime.now()
    project_dict = {'project_name':project_name,'key_phrases':key_phrases,'created_time':started_time,'state':'queued'}
    record_entry = mycol.insert_one(project_dict)
    print("Project stored in db: ", record_entry.inserted_id)
    print("Adding to projects queue")
    add_to_projects_queue([record_entry.inserted_id])

# create_and_queue_project('Educational softwares project',['Hazard management'])
# get_projects_via_queue()

# print(process_queries(['medical management system']))