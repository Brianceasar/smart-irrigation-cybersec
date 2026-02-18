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
SOIL_TOPIC = "irrigation/soil"
CONTROL_TOPIC = "irrigation/control"

DEVICE_ID = "irrigation-node-01"
MOISTURE_THRESHOLD = 50

manual_override = False
manual_state = None 

# ===============================
# MQTT Callbacks
# ===============================

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[+] Connected to MQTT Broker")
        client.subscribe(CONTROL_TOPIC)
    else:
        print("[-] Connection failed")

def on_message(client, userdata, msg):
    global manual_override, manual_state

    try:
        data = json.loads(msg.payload.decode())

        if data.get("command") == "ON":
            manual_override = True
            manual_state = "ON"
            print("[MANUAL] Pump forced ON")

        elif data.get("command") == "OFF":
            manual_override = True
            manual_state = "OFF"
            print("[MANUAL] Pump forced OFF")

        elif data.get("command") == "AUTO":
            manual_override = False
            manual_state = None
            print("[MANUAL] Returning to automatic mode")

    except Exception as e:
        print("Error processing control message:", e)


# ===============================
# MQTT Setup
# ===============================

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, BROKER_PORT, 60)

client.loop_start()

# ===============================
# Simulation Loop
# ===============================

try:
    while True:
        soil_moisture = random.randint(20, 90)
        temperature = random.randint(18, 35)
        humidity = random.randint(40, 90)
        water_level = random.randint(30, 100)

        if manual_override:
            pump_state = manual_state
            print(f"[OVERRIDE] Pump state: {pump_state}")

        else:
            if soil_moisture < MOISTURE_THRESHOLD:
                pump_state = "ON"
                print("[AUTO] Soil dry → Pump ON")
            else:
                pump_state = "OFF"
                print("[AUTO] Soil wet → Pump OFF")

        payload = {
            "device_id": DEVICE_ID,
            "soil_moisture": soil_moisture,
            "temperature": temperature,
            "humidity": humidity,
            "water_level": water_level,
            "pump_state": pump_state,
            "mode": "Automatic",
            "led_state": pump_state,
            "timestamp": time.time()
        }

        message = json.dumps(payload)

        client.publish(SOIL_TOPIC, message)

        print(f"[+] Publishing: {message}")
        print("-" * 60)

        time.sleep(5)

except KeyboardInterrupt:
    print("\n[!] Simulation stopped")

finally:
    client.loop_stop()
    client.disconnect()