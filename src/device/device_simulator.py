import paho.mqtt.client as mqtt
import time
import random

BROKER = "172.16.187.130"
PORT = 1883

DEVICE_ID = "irrigation-node-01"
SOIL_TOPIC = "irrigation/soil"
COMMAND_TOPIC = "irrigation/command"

def on_connect(client, userdata, flags, rc):
    print("[+] connected to broker")
    client.subscribe(COMMAND_TOPIC)
    
def on_message(client, userdata, msg):
    print(f"[!] Command recieved: {msg.payload.decode()}")
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    soil_moisture = random.randint(30, 80)
    payload = f"{DEVICE_ID}:{soil_moisture}"
    print(f"[+] Publishing soil moisture: {payload}")
    client.publish(SOIL_TOPIC, payload)
    print(f"[+] Published: {payload}")
    time.sleep(5)