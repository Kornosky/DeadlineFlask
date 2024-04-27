import datetime
import os
from collections import defaultdict
from typing import Collection, List, OrderedDict

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient


def create_app():
    app = Flask(__name__)
    client: MongoClient = MongoClient(os.getenv("MONGODB_URI"))
    app.db: Database = client.deadline10db  # Sample data for the table
    
    jobs = [
        {"name": "Job 1", "priority": 10, "project": "A"},
        {"name": "Job 2", "priority": 20, "project": "A"},
        {"name": "Job 3", "priority": 30, "project": "B"},
        # Add more elements as needed
    ]

    # @app.route('/get_data', methods=['GET'])
    # def get_data():
    #     # For when I begin making ajax calls to the mongo
    #     collection = jobs
    #     data = collection.find()  # Retrieve data from MongoDB collection
    #     return jsonify(list(data))

    @app.route("/")
    def home():
        list_of_jobs: List[dict] = list(app.db["Jobs"].find({}))
        
        # Unpack the Props field and cull unneeded columns
        column_list = ["Name", "Plug", "Status", "DateComp", "Date"]
        final_list_of_jobs = list()
        for j in list_of_jobs:
            j.update(j['Props'])
            
            # Add custom fields
            status = "Unknown"
            total_chunks = j['CompletedChunks'] + j['RenderingChunks'] + j['FailedChunks'] + j['PendingChunks'] + j['QueuedChunks'] # Unsure if need this info
            if j['RenderingChunks']:
                status = "Rendering"
            elif j['FailedChunks']:
                status = "Failing"
            elif j["QueuedChunks"]:
                status = "Queued"
            else:
                status = "Completed"
            j["Status"] = status
            
            excluded_keys = [column for column in j.keys() if column not in column_list]
            for column in excluded_keys:
                del j[column]        
            
            ### Post-Custom Data Styling
            # Make dates more legible to the layman
            for key, value in j.items():
                if isinstance(value, datetime.datetime):
                    j[key] = value.strftime('%b %d %I:%M %p')

            # Reorder dict
            # Create a new dictionary with pairs in the desired order

            final_list_of_jobs.append(OrderedDict({key: j[key] for key in column_list if key in j}))
        print(final_list_of_jobs)
        
        return render_template("home.html", jobs=final_list_of_jobs)

    return app