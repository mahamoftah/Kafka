from confluent_kafka import Producer

def prod1(data): 

    me = 'maha-moftah-prod1'
    conf = {'bootstrap.servers': '34.68.55.43:9094,34.136.142.41:9094,34.170.19.136:9094'}

    producer = Producer(conf)

    topic = me

    producer.produce(topic, key="key", value=data)

    producer.flush()
    print("Producer 1")