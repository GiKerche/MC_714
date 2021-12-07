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
    time.sleep(15)#tempo para acessar e modificar variável que a outra máquina também tem acesso
 
def on_message(client, userdata, message):
    global is_doing_critical
    global is_waiting_availability
    msg=str(message.payload.decode("utf-8")) #decodifica a mensagem
    topics=(message.topic).split("/")
    if topics[1]=="client_a": #para a máquina atual
        if(msg=="AVAILABLE"): # recurso A não tá fazendo
            is_doing_critical=True
            print("CLIENT pode fazer a sessão critica")
            is_waiting_availability=False
 
        elif(msg=="REQUEST"): #requisição da outra máquina
            response= "AVAILABLE" if (not is_doing_critical) else "NONAVAILABLE" #verifica se está disponível ou não para dar resposta
            print("Recebeu pedido para fazer sessão critica, resposta ", response)
            client.publish("mutual/client_b/exclusion",response)#publica a mensagem para b
       
        elif(msg=="NONAVAILABLE"):
            print("pedido para fzer sessão critica negado, tentando dnv em 10s") #Fez a requisição e recebeu resposta negativa
            time.sleep(10) #espera 10 segundos para requisitar de novo
            response= "REQUEST"
            client.publish("mutual/client_b/exclusion",response)
 
   
   
def on_publish(client, userdata, mid):
    logging.info("message published "  +str(mid))
 
process_id="A"
 
send_topic ="mutual/client_b/" +home_topic
 
client= mqtt.Client(f"Client{process_id}",False)   #cria cliente objeto
client.on_subscribe = on_subscribe  
client.on_disconnect = on_disconnect
client.on_connect = on_connect
client.on_message=on_message
client.connect(broker,port) #estabelece conexão
time.sleep(1)
client.loop_start()
client.subscribe("mutual/#")
chance_of_triggering_critical_session=0.5 #chance para enviar requisição
is_doing_critical=False
is_waiting_availability=False
while True: #roda sempre, para break with CTRL+C
    random_number=random.random() #número aleatório
 
    if(is_doing_critical): #se tem sessão crítica para começar
        print("começando sessão critica")
        criticalSession()# faz sessão crítica
        print("sessão critica concluida")
        is_doing_critical=False
    if(not is_waiting_availability and random_number>1-chance_of_triggering_critical_session): # se está na sua vez de fazer requisição pelas regras definidas
        print("sending request") #envia requisição
        client.publish(send_topic,"REQUEST")
        is_waiting_availability=True
    time.sleep(1)
client.disconnect()
 
client.loop_stop()
