from confluent_kafka import Consumer, KafkaError, KafkaException
import random
import requests
import json
from ultralytics import YOLO
import torch
from consumer2 import consum2
from producer2 import prod2
from producer1 import prod1

torch.cuda.empty_cache()

me = 'maha-moftah-prod1'
conf = {'bootstrap.servers': '34.68.55.43:9094,34.136.142.41:9094,34.170.19.136:9094',
        'group.id': 'foo',
        'auto.offset.reset': 'smallest'}

consumer = Consumer(conf)

running = True

def detect_object(id, filename):
    model = YOLO("yolov8n.pt")
    results = model('http://127.0.0.1:5000/images/' + filename)
    print("Maha")
    for result in results: 
        boxes = result.boxes
        print(boxes)
        for box in boxes: 
            return model.names.get(box.cls.item())
    

def basic_consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)
        print("Subscribe To Topics", topics)

        while running:
            print("loop1")

            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                print("Consumer 1")                

                msg_dict = json.loads(msg.value())
                id = msg_dict['id']
                filename = msg_dict['filename']

                requests.put('http://127.0.0.1:5000/object/' + id, json={"object": detect_object(id, filename)})

                # response = requests.post('http://127.0.0.1:5000/refresh')
                # print(response.text)

                msg = {"filename": filename, "id": id}
                data = json.dumps(msg)
                prod2(data)
                consum2()

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False

basic_consume_loop(consumer, [me])