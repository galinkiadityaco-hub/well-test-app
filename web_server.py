from flask import Flask,Response,request
from queue import Queue
import json

app=Flask(__name__)
data_queue=Queue()

@app.route("/push",methods=["POST"])
def push_data():
    data=request.json
    print(f"Received data: {data}")
    data_queue.put(data)
    return {"status" : "ok"}

@app.route("/stream")
def stream():
    def event_stream():
        while True:
            data=data_queue.get()
            yield f"data: {json.dumps(data)}\n\n"
    return Response(event_stream(),mimetype="text/event-stream")

@app.route("/")
def home():
    return app.send_static_file("Test_result_webpage.html")

app.run(port=5000,debug=True,threaded=True)