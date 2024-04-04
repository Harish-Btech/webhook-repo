from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")  # Update with your MongoDB connection URI
db = client["github_webhooks"]
collection = db["events"]

@app.route('/webhook', methods=['POST'])
def webhook_receiver():
    if request.method == 'POST':
        data = request.json
        event_data = {
            "_id": data["pull_request"]["id"] if data["action"] == "pull_request" else data["sha"],
            "author": data["sender"]["login"],
            "action": data["action"],
            "from_branch": data["pull_request"]["head"]["ref"] if data["action"] == "pull_request" else None,
            "to_branch": data["pull_request"]["base"]["ref"] if data["action"] == "pull_request" else data["ref"],
            "timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }
        collection.insert_one(event_data)
        return "Webhook received successfully", 200
    else:
        return "Method Not Allowed", 405

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {"_id": 0}))  # Exclude _id field from response
    return jsonify(events), 200

if __name__ == '__main__':
    app.run(debug=True)
