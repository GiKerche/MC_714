import paho.mqtt.client as mqtt
import time,logging
import random
broker="3.88.68.202"
home_topic="exclusion"
port=1883
QOS=0
 
count=0
 
CLEAN_SESSION=True
logging.basicConfig(level=logging.INFO)
#mesma lógica da outra máquina
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
 
def criticalSession():
    time.sleep(15)
 
def on_message(client, userdata, message):
    global is_doing_critical
    global is_waiting_availability
    msg=str(message.payload.decode("utf-8"))
    topics=(message.topic).split("/")
    if topics[1]=="client_b":
        if(msg=="AVAILABLE"):
            is_doing_critical=True
            print("CLIENT pode fazer a sessão critica")
            is_waiting_availability=False
 
        elif(msg=="REQUEST"):
            response= "AVAILABLE" if (not is_doing_critical and not is_waiting_availability ) else "NONAVAILABLE"
            print("Recebeu pedido para fazer sessão critica, resposta ", response)
            client.publish("mutual/client_a/exclusion",response)
       
        elif(msg=="NONAVAILABLE"):
            print("pedido para fzer sessão critica negado, tentando dnv em 10s")
            time.sleep(10)
            response= "REQUEST"
            client.publish("mutual/client_a/exclusion",response)
 
        elif(is_waiting_availability and msg=="FINISHED"):
            is_doing_critical=True
            is_waiting_availability=False
   
def on_publish(client, userdata, mid):
    logging.info("message published "  +str(mid))
 
process_id="B"
 
send_topic ="mutual/client_a/" +home_topic
 
client= mqtt.Client(f"Client{process_id}",False)    
client.on_subscribe = on_subscribe  
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message=on_message
client.connect(broker,port)          
time.sleep(1)
client.loop_start()
client.subscribe("mutual/#")
chance_of_triggering_critical_session=0.5
is_doing_critical=False
is_waiting_availability=False
while True:
    random_number=random.random()
    if(is_doing_critical):
        print("começando sessão critica")
        criticalSession()
        print("sessão critica concluida")
        is_doing_critical=False
    if(not is_waiting_availability and random_number>1-chance_of_triggering_critical_session):
        print("sending request")
        client.publish(send_topic,"REQUEST")
        is_waiting_availability=True
    time.sleep(1)
client.disconnect()
client.loop_stop()
 
