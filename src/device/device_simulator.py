import paho.mqtt.client as mqtt
import time
import random
import json

BROKER = "172.16.187.130"
PORT = 1883

DEVICE_ID = "irrigation-node-01"
SOIL_TOPIC = "irrigation/soil"
COMMAND_TOPIC = "irrigation/command"

def on_connect(client, userdata, flags, rc):
    print("[+] connected to broker")
    client.subscribe(COMMAND_TOPIC)
    
def on_message(client, userdata, msg):
    command = msg.payload.decode()
    print(f"[!] Command received: {command}")

    if command == "PUMP_ON":
        print("[!!!] Irrigation pump ACTIVATED")
    elif command == "PUMP_OFF":
        print("[---] Irrigation pump DEACTIVATED")
    else:
        print("[?] Unknown command received")
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

while True:
    soil_moisture = random.randint(30, 80)

    payload = {
        "device_id": DEVICE_ID,
        "soil_moisture": soil_moisture,
        "timestamp": time.time()
    }

    print(f"[+] Publishing: {payload}")

    client.publish(SOIL_TOPIC, json.dumps(payload))

    if soil_moisture < 40:
        print("[AUTO] Soil dry → Pump ON")
    elif soil_moisture > 70:
        print("[AUTO] Soil wet → Pump OFF")

    time.sleep(5)
