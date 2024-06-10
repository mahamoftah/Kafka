import os
import random
import sqlite3
import sys
import uuid
from producer1 import prod1
from flask import Flask, request, jsonify
import os
from flask_sock import Sock

from flask import (Flask, redirect, render_template_string, request,
                   send_from_directory)

IMAGES_DIR = "images"
MAIN_DB = "main.db"

app = Flask(__name__)
sock = Sock(app)


def get_db_connection():
    conn = sqlite3.connect(MAIN_DB)
    conn.row_factory = sqlite3.Row
    return conn

con = get_db_connection()
con.execute("CREATE TABLE IF NOT EXISTS image(id, filename, object)")
if not os.path.exists(IMAGES_DIR):
   os.mkdir(IMAGES_DIR)

@app.route('/', methods = ['GET'])
def index():
   con = get_db_connection()
   cur = con.cursor()
   res = cur.execute("SELECT * FROM image")
   images = res.fetchall()
   con.close()
   return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<style>
.container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  grid-auto-rows: minmax(100px, auto);
  gap: 20px;
}
img {
   display: block;
   max-width:100%;
   max-height:100%;
   margin-left: auto;
   margin-right: auto;
}
.img {
   height: 270px;
}
.label {
   height: 30px;
  text-align: center;
}
</style>
</head>
<body>
<form method="post" enctype="multipart/form-data">
  <div>
    <label for="file">Choose file to upload</label>
    <input type="file" id="file" name="file" accept="image/x-png,image/gif,image/jpeg" />
  </div>
  <div>
    <button>Submit</button>
  </div>
</form>
<div class="container">
{% for image in images %}
<div>
<div class="img"><img src="/images/{{ image.filename }}"></img></div>
<div class="label">{{ image.object | default('undefined', true) }}</div>
</div>
{% endfor %}
</div>
                                 
      <script> 

         const exampleSocket = new WebSocket("ws://127.0.0.1:5000/connect");
                                 
         exampleSocket.onopen = (event) => {
            console.log('WebSocket connection opened.');
         };

         exampleSocket.onmessage = (event) => {
            console.log('Received message: ${event.data}');
            if (event.data == 'restart'){
               alert("Refreshing!");
               location.reload();
            }                        
         };
                                                            
      </script>
                                 
</body>
</html>
   """, images=images)

@app.route('/images/<path:path>', methods = ['GET'])
def image(path):
    return send_from_directory(IMAGES_DIR, path)

@app.route('/object/<id>', methods = ['PUT'])
def set_object(id):
   con = get_db_connection()
   cur = con.cursor()
   json = request.json
   object = json['object']
   cur.execute("UPDATE image SET object = ? WHERE id = ?", (object, id))
   con.commit()
   con.close()
   return '{"status": "OK"}'

import json

@app.route('/', methods = ['POST'])
def upload_file():
   f = request.files['file']
   ext = f.filename.split('.')[-1]
   id = uuid.uuid4().hex
   filename = "{}.{}".format(id, ext)
   f.save("{}/{}".format(IMAGES_DIR, filename))
   con = get_db_connection()
   cur = con.cursor()
   cur.execute("INSERT INTO image (id, filename, object) VALUES (?, ?, ?)", (id, filename, ""))
   con.commit()
   msg = {"filename": filename, "id": id}
   data = json.dumps(msg)
   prod1(data)
   con.close()
   return redirect('/')


current_ws = None
@app.route('/refresh', methods=['POST'])
def refresh_page():
    global current_ws
    if current_ws is None:
        return jsonify({'error': 'No active WebSocket connection'}), 400
    else:
        current_ws.send('restart')
        return jsonify({'message': 'Refresh command sent'}), 200


@sock.route('/connect')
def connection(ws):
   global current_ws
   current_ws = ws
   print("ok miho")
   return jsonify({'message': 'WebSocket connected'}), 200

		
if __name__ == '__main__':
   app.run(debug = True, port=(int(sys.argv[1]) if len(sys.argv) > 1 else 5000))