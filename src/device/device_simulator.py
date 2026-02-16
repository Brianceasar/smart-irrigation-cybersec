#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import time
import random

# ===============================
# Configuration
# ===============================

BROKER_IP = "172.16.187.130"   # Your Ubuntu Server IP
BROKER_PORT = 1883
TOPIC = "irrigation/soil"

DEVICE_ID = "irrigation-node-01"
MOISTURE_THRESHOLD = 50

# ===============================
# MQTT Setup
# ===============================

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[+] Connected to MQTT Broker")
    else:
        print("[-] Failed to connect")

client.on_connect = on_connect

client.connect(BROKER_IP, BROKER_PORT, 60)

client.loop_start()

# ===============================
# Simulation Loop
# ===============================

try:
    while True:
        # Simulate soil moisture reading
        soil_moisture = random.randint(20, 90)

        # Automatic pump logic
        if soil_moisture < MOISTURE_THRESHOLD:
            pump_state = "ON"
            print("[AUTO] Soil dry → Pump ON")
        else:
            pump_state = "OFF"
            print("[AUTO] Soil wet → Pump OFF")

        # Construct JSON payload
        payload = {
            "device_id": DEVICE_ID,
            "soil_moisture": soil_moisture,
            "pump_state": pump_state,
            "timestamp": time.time()
        }

        # Convert to valid JSON
        message = json.dumps(payload)

        # Publish
        client.publish(TOPIC, message)

        print(f"[+] Publishing: {message}")
        print("-" * 50)

        time.sleep(5)

except KeyboardInterrupt:
    print("\n[!] Simulation stopped")

finally:
    client.loop_stop()
    client.disconnect()
