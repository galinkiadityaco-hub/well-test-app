import os
import json
from flask import Flask, Response, request
from queue import Queue

# Note: static_folder='static' tells Flask where your HTML file is
app = Flask(__name__, static_folder='static')
data_queue = Queue()

# We store a history so if someone joins late, they see the previous results
history = []

# SECURITY: Only requests with this key can update the table
# We will set this "MY_SECRET_KEY" in the Render Dashboard later
API_KEY = os.environ.get("MY_SECRET_KEY", "local_dev_key")

@app.route("/push", methods=["POST"])
def push_data():
    # Check for the secret key in headers
    if request.headers.get("X-API-KEY") != API_KEY:
        return {"status": "unauthorized"}, 403

    data = request.json
    print(f"Received data: {data}")
    
    # Save to history (keep last 50 entries)
    history.append(data)
    if len(history) > 50: history.pop(0)
    
    data_queue.put(data)
    return {"status": "ok"}

@app.route("/stream")
def stream():
    def event_stream():
        # First, send everything in history to the new user
        for item in history:
            yield f"data: {json.dumps(item)}\n\n"
        
        # Then, wait for new live data
        while True:
            data = data_queue.get()
            yield f"data: {json.dumps(data)}\n\n"
            
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/")
def home():
    # This serves your HTML file to anyone who visits the site
    return app.send_static_file("Test_result_webpage.html")

if __name__ == "__main__":
    # Render assigns a dynamic port, we must capture it
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)
