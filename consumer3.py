
def consum3():

    from confluent_kafka import Consumer, KafkaError, KafkaException
    import requests


    me = 'maha-moftah-prod3'
    conf = {'bootstrap.servers': '34.68.55.43:9094,34.136.142.41:9094,34.170.19.136:9094',
            'group.id': 'foo',
            'auto.offset.reset': 'smallest'
        }

    consumer = Consumer(conf)

    running = True

    def basic_consume_loop(consumer, topics):
        try:
            consumer.subscribe(topics)
            print("Subscribe To Topics", topics)
            
            while running:
                print("loop3")

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
                    print("Consumer 3") 

                    requests.post('http://127.0.0.1:5000/refresh')
                    shutdown()

        finally:
            # Close down consumer to commit final offsets.
            consumer.close()


    def shutdown():
        global running
        running = False

    basic_consume_loop(consumer, [me])