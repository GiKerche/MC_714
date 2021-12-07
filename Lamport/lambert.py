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
 
def on_subscribe(client, userdata, mid, granted_qos):  
   # Mesmo código da parte de comunicação
    time.sleep(1)
    logging.info("sub acknowledge message id="+str(mid))  
    pass
 
def on_disconnect(client, userdata,rc=0):
# Mesmo código da parte de comunicação
    logging.info("DisConnected result code "+str(rc))
 
def on_connect(client, userdata, flags, rc):
    # Mesmo código da parte de comunicação
    logging.info("Connected flags"+str(flags)+"result code "+str(rc))
 
def get_ts(message):
    #Pega a parte da mensagem com o contador
    return int(message.split(',')[0].split("ts=")[1])
 
def on_message(client, userdata, message):
    global count
    #Decodifica a mensagem
    msg=str(message.payload.decode("utf-8"))
    topics=(message.topic).split("/")
    print("Received message '" + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos),"retain",str(message.retain))
   
 
    if topics[1]=="client_a":#pega a msg no tópico para a própria máquina
        message_ts=get_ts(msg)
        count = max(count,message_ts) #verifica qual contador é maior, se for o da outra máquina, troca por ele
   
   
def on_publish(client, userdata, mid):
# Mesmo código da parte de comunicação
    logging.info("message published "  +str(mid))
 
def evento(count): # Simulação de evento
    print(f"evento aconteceu, counter de {count} pra {count+1}")
 
process_id="A"
send_topic ="lambert/client_b/" +home_topic # tópico da comunicação
client= mqtt.Client(f"Client{process_id}",False) #cria o objeto cliente
client.on_subscribe = on_subscribe  
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message=on_message
client.connect(broker,port) #estabelece conexão
time.sleep(1)
client.loop_start()
client.subscribe("lambert/#")
chance_of_sending_message=0.3
while True: #roda sempre até parada via terminal, sem condição de parada
   evento(count) #evento ocorre
   count+=1 #contador lógico atualiza
   random_number=random.random() #defini número randômico
   if(random_number>1-chance_of_sending_message): #verifica se está dentro da probabilidade definida
    msg=f"ts={count}, from {process_id} hi XD" #mensagem que será enviada
    print(f"Client {process_id} is sending message, counter {count}")
    client.publish(send_topic,msg) #publica mensagem no tópico
   time.sleep(10)
client.disconnect()
 
client.loop_stop()
 
