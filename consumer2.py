from confluent_kafka import Consumer, KafkaError, KafkaException
import random
import requests
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
from consumer3 import consum3
import json
from producer3 import prod3
from producer1 import prod1

def consum2():

    me = 'maha-moftah-prod2'
    conf = {'bootstrap.servers': '34.68.55.43:9094,34.136.142.41:9094,34.170.19.136:9094',
            'group.id': 'foo',
            'auto.offset.reset': 'smallest'
    }

    consumer = Consumer(conf)

    running = True

    def add_watermark(id, filename):

        data = requests.get(f'http://127.0.0.1:5000/images/' + filename).content 

        # Save the image temporarily
        with open('img.jpg', 'wb') as f:
            f.write(data) 

        # Open the image
        img = Image.open('img.jpg')

        # Create a copy of the image to add the watermark
        new_image = img.copy()
        
        # Initialize ImageDraw
        draw = ImageDraw.Draw(new_image)
        
        # Get image dimensions
        w, h = img.size
        x, y = int(w / 2), int(h / 2)

        # Determine the font size based on ismage dimensions
        font_size = min(x, y) // 6
        
        # Load the font
        font = ImageFont.truetype("arial.ttf", font_size)
        
        # Get the watermark text
        watermark_text = "Kafka"
        
        # Add the text to the image
        draw.text((x, y), watermark_text, fill=(0, 0, 0), font=font, anchor='ms')
        new_image.save("{}/{}".format("images", filename))


    def basic_consume_loop(consumer, topics):
        try:
            consumer.subscribe(topics)
            print("Subscribe To Topics", topics)

            while running:
                print("loop2")
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

                    print("Consumer 2") 

                    msg_dict = json.loads(msg.value())
                    id = msg_dict['id']
                    filename = msg_dict['filename']

                    add_watermark(id, filename)
                    
                    prod3("Refresh Please")
                    consum3()
                    shutdown()
                    
        finally:
            # Close down consumer to commit final offsets.
            consumer.close()


    def shutdown():
        global running
        running = False

    basic_consume_loop(consumer, [me])