#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import time
import random

# ===============================
# Configuration
# ===============================

BROKER_IP = "172.16.187.130"
BROKER_PORT = 1883

TOPIC_DATA = "irrigation/soil"
TOPIC_CONTROL = "irrigation/control"
TOPIC_MODE = "irrigation/mode"

DEVICE_ID = "irrigation-node-01"
MOISTURE_THRESHOLD = 50

pump_state = "OFF"
system_mode = "AUTO"

# ===============================
# MQTT Callbacks
# ===============================

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[+] Connected to MQTT Broker")
        client.subscribe(TOPIC_CONTROL)
        client.subscribe(TOPIC_MODE)
    else:
        print("[-] Connection failed")

def on_message(client, userdata, msg):
    global pump_state
    global system_mode

    try:
        data = json.loads(msg.payload.decode())

        # Handle Mode Change
        if msg.topic == TOPIC_MODE:
            system_mode = data.get("mode", "AUTO")
            print(f"[MODE] Changed to {system_mode}")

        # Handle Manual Pump Control
        elif msg.topic == TOPIC_CONTROL and system_mode == "MANUAL":
            command = data.get("command")

            if command == "ON":
                pump_state = "ON"
            elif command == "OFF":
                pump_state = "OFF"

            print(f"[MANUAL] Pump forced {pump_state}")

    except Exception as e:
        print("Error:", e)

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

        # Automatic logic only when in AUTO mode
        if system_mode == "AUTO":
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
            "mode": system_mode,
            "timestamp": time.time()
        }

        client.publish(TOPIC_DATA, json.dumps(payload))

        print(f"[DATA] {payload}")
        print("-" * 60)

        time.sleep(5)

except KeyboardInterrupt:
    print("\n[!] Simulation stopped")

finally:
    client.loop_stop()
    client.disconnect()
