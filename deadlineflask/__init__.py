import datetime
import json
import os
from collections import defaultdict
from typing import Collection, Dict, List, OrderedDict

from dotenv import load_dotenv
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)
from pymongo import MongoClient

# Assuming you have a persistent store to keep track of the last update time
last_update_time = None

def calculate_farm_health() -> str:
    import random
    
    rngNumber = random.randint(0,10)
    if rngNumber > 7:
        return "Excellent"
    if rngNumber > 3:
        return "Normal"
    else:         
        return "Good"


# Define what makes up a "farm"
farmStatuses: Dict = {
    "Farm Health": calculate_farm_health,
    "Overall Farm": calculate_farm_health,
    "Comp Farm": calculate_farm_health,
}


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'

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

    @app.route("/update_config", methods=["POST"])
    def update_config():
        data = request.json
        session["user_config"] = data
        return "User config updated successfully"


    @app.route("/update_data", methods=["GET"])
    def update_data():
        global last_update_time
        
        # Fetch updated data from your database or any other source
        updated_data = {
            "Farm Health": calculate_farm_health(),
            "Overall Farm": calculate_farm_health(),
            "Comp Farm": calculate_farm_health(),
            "Jobs": fetch_mongo_job_data(),  # Assuming you have updated data here
        }
        
        # Calculate time since last update
        if last_update_time:
            time_since_last_update = datetime.datetime.now() - last_update_time
            updated_data["Time Since Last Update"] = str(f"{time_since_last_update.total_seconds():.0f} Seconds")
        else:
            updated_data["Time Since Last Update"] = "No previous update"
        
        # Update last update time
        last_update_time = datetime.datetime.now()
        
        # Return updated data as JSON response
        return json.dumps(updated_data)


    @app.route("/")
    def home():
        if "user_config" not in session:
            session["user_config"] = {}  # Initialize user config

        final_list_of_jobs = fetch_mongo_job_data()

        return render_template(
            "home.html", jobs=final_list_of_jobs, farmStatuses=farmStatuses
        )

    def fetch_mongo_job_data():
        list_of_jobs: List[Dict] = list(app.db["Jobs"].find({}))

        # Unpack the Props field and cull unneeded columns
        friendly_naming_mapping = {
            "_id": "ID",
            "Name": "Name",
            "Plug": "Plugin",
            "Status": "Status",
            "DateComp": "Completed At",
            "Date": "Submitted At",
        }
        desired_column_list = ["_id", "Name", "Plug", "Status", "DateComp", "Date"]

        final_list_of_jobs: List[Dict] = list()
        for j in list_of_jobs:
            j.update(j["Props"])
            
            # Add custom fields
            status = "Unknown"
            total_chunks = (
                j["CompletedChunks"]
                + j["RenderingChunks"]
                + j["FailedChunks"]
                + j["PendingChunks"]
                + j["QueuedChunks"]
            )  # Unsure if need this info
            if j["RenderingChunks"]:
                status = "Rendering"
            elif j["FailedChunks"]:
                status = "Failing"
            elif j["QueuedChunks"]:
                status = "Queued"
            else:
                status = "Completed"
            j["Status"] = status

            excluded_keys = [
                column for column in j.keys() if column not in desired_column_list
            ]

            for column in excluded_keys:
                del j[column]

            ### Post-Custom Data Styling
            # Make dates more legible to the layman
            zero_datetime = datetime.datetime(1, 1, 1, 0, 0, 0)
            for key, value in j.items():
                if isinstance(value, datetime.datetime):
                    if value != zero_datetime:
                        j[key] = value.strftime("%b %d %I:%M %p")
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
            from pprint import pprint

            final_list_of_jobs.append(mapped_job)
        return final_list_of_jobs

    return app


"""
TODO Tests:
If friendly mapping is missing, dont break things
"""
