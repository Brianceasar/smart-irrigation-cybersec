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
# Environmental State (PERSISTENT)
# ===============================

soil_moisture = 55.0
temperature = 28.0
humidity = 60.0
water_level = 80.0

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

        # Mode change
        if msg.topic == TOPIC_MODE:
            system_mode = data.get("mode", "AUTO")
            print(f"[MODE] Changed to {system_mode}")

        # Manual pump control
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

        # ===============================
        # Environmental drift
        # ===============================
        temperature += random.uniform(-0.3, 0.3)
        humidity += random.uniform(-0.8, 0.8)

        temperature = max(15, min(45, temperature))
        humidity = max(20, min(95, humidity))

        # ===============================
        # Soil physics model
        # ===============================
        if pump_state == "ON":
            soil_moisture += 2.2
            water_level -= 0.4
        else:
            evap_rate = (temperature / 100.0) * (1 - humidity / 100.0)
            soil_moisture -= evap_rate * 3.5

        # slow natural refill of tank
        water_level += 0.05

        # Clamp values
        soil_moisture = max(0, min(100, soil_moisture))
        water_level = max(0, min(100, water_level))

        # ===============================
        # AUTO control logic
        # ===============================
        if system_mode == "AUTO":
            if soil_moisture < MOISTURE_THRESHOLD:
                pump_state = "ON"
                print("[AUTO] Soil dry → Pump ON")
            else:
                pump_state = "OFF"
                print("[AUTO] Soil wet → Pump OFF")

        # ===============================
        # Payload
        # ===============================
        payload = {
            "device_id": DEVICE_ID,
            "soil_moisture": int(soil_moisture),
            "temperature": int(temperature),
            "humidity": int(humidity),
            "water_level": int(water_level),
            "pump_state": pump_state,
            "mode": system_mode,
            "timestamp": int(time.time())
        }

        client.publish(TOPIC_DATA, json.dumps(payload))

        print(
            f"[STATE] Soil:{soil_moisture:.1f}% | "
            f"Temp:{temperature:.1f}C | "
            f"Hum:{humidity:.1f}% | "
            f"Pump:{pump_state} | Mode:{system_mode}"
        )
        print("-" * 60)

        time.sleep(5)

except KeyboardInterrupt:
    print("\n[!] Simulation stopped")

finally:
    client.loop_stop()
    client.disconnect()
