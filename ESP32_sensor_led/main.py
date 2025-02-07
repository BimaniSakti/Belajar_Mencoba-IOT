from machine import Pin
from time import sleep
import dht

led = Pin(4, Pin.OUT)
sensor = dht.DHT11(Pin(5))

while True:
    sensor.measure()
    try:
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        print(f"suhu : {temperature}, kelembapan : {humidity}")
        if temperature <= 20 or humidity >= 70:
            led.on()
        else:
            led.off()
        sleep(0.5)
    except Exception as e:
        print(f"Error: {e}")