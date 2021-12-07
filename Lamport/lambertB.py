import paho.mqtt.client as mqtt
import time,logging
import random
broker="54.83.107.70"
home_topic="clock"
port=1883
QOS=0
count=0
CLEAN_SESSION=True
logging.basicConfig(level=logging.INFO)
# mesmo funcionamento da máquina A
def on_subscribe(client, userdata, mid, granted_qos):
   time.sleep(1)
   logging.info("sub acknowledge message id="+str(mid))
   pass
 
def on_disconnect(client, userdata,rc=0):
    logging.info("DisConnected result code "+str(rc))
 
def on_connect(client, userdata, flags, rc):
    logging.info("Connected flags"+str(flags)+"result code "+str(rc))
 
def get_ts(message):
    return int(message.split(',')[0].split("ts=")[1])
 
def on_message(client, userdata, message):
    global count
    msg=str(message.payload.decode("utf-8"))
    topics=(message.topic).split("/")
    print("Received message '" + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos),"retain",str(message.retain))
   
 
    if topics[1]=="client_b":  #verifica se é para ele a mensagem
        message_ts=get_ts(msg)
        count = max(count,message_ts)
   
   
def on_publish(client, userdata, mid):
    logging.info("message published "  +str(mid))
 
def evento(count):
    print(f"evento aconteceu, counter de {count} pra {count+1}")
 
process_id="B" #define como o outro processo
 
send_topic ="lambert/client_a/" +home_topic # tópico da comunicação
 
client= mqtt.Client(f"Client{process_id}",False)
client.on_subscribe = on_subscribe  
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message=on_message
client.connect(broker,port)          
time.sleep(1)
client.loop_start()
client.subscribe("lambert/#")
chance_of_sending_message=0.3
while True:
   evento(count)
   count+=1
   random_number=random.random()
   if(random_number>1-chance_of_sending_message):
    msg=f"ts={count}, from {process_id} hi XD"
    print(f"Client {process_id} is sending message, counter {count}")
    client.publish(send_topic,msg)
   time.sleep(5)
client.disconnect()
 
client.loop_stop()
