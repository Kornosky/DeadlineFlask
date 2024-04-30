import datetime
import os
from collections import defaultdict
from typing import Collection, Dict, List, OrderedDict

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient

# Define what makes up a "farm"
farmStatuses: Dict = {
    "Farm Health": "Good",
    "Overall Farm": "Busy",
    "Comp Farm": "Full"
}



def create_app():
    app = Flask(__name__)
    client: MongoClient = MongoClient(os.getenv("MONGODB_URI"))
    app.db: Database = client.deadline10db  # Sample data for the table
    
    jobs: Dict = [
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
        list_of_jobs: List[Dict] = list(app.db["Jobs"].find({}))
        
        # Unpack the Props field and cull unneeded columns
        friendly_naming_mapping = {
            "Name": "Name",
            "Plug": "Plugin",
            "Status": "Status",
            "DateComp": "Completed At",
            "Date": "Submitted At",
        }
        desired_column_list = ["Name", "Plug", "Status", "DateComp", "Date"]
        
        final_list_of_jobs: List[Dict] = list()
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
            
            excluded_keys = [column for column in j.keys() if column not in desired_column_list]
            
            for column in excluded_keys:
                del j[column]        
            
            ### Post-Custom Data Styling
            # Make dates more legible to the layman
            zero_datetime = datetime.datetime(1, 1, 1, 0, 0, 0)
            for key, value in j.items():
                if isinstance(value, datetime.datetime):
                    if value != zero_datetime:
                        j[key] = value.strftime('%b %d %I:%M %p')
                    else:
                        j[key] = "-"

            # Reorder dict and map the friendly names (if mapping exists)
            mapped_job = OrderedDict()
            for column in desired_column_list:
                if column in j:
                    if column in friendly_naming_mapping:
                        mapped_job[friendly_naming_mapping[column]] = j[column]
                    else:
                        mapped_job[column] = j[column]
            
            final_list_of_jobs.append(mapped_job)
                

            
        print(final_list_of_jobs)
        print(farmStatuses)
        return render_template("home.html", jobs=final_list_of_jobs, farmStatuses=farmStatuses)

    return app

"""
TODO Tests:
If friendly mapping is missing, dont break things
"""