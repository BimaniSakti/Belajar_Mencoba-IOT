import network
import time
from machine import Pin
import dht
import ujson
from umqtt.simple import MQTTClient

# Parameter MQTT Server
MQTT_CLIENT_ID      = "UNI473/RisangHaryo"
MQTT_BROKER         = "broker.emqx.io"
MQTT_USER           = ""
MQTT_PASSWORD       = ""
MQTT_PUB_TOPIC      = "/UNI473/RisangHaryoPamungkasBimaniSakti/data_sensor"
MQTT_SUB_TOPIC      = "/UNI473/RisangHaryoPamungkasBimaniSakti/aktuasi_led"

# Mendefinisikan sensor
sensor = dht.DHT22(Pin(2))

# Mendefinisikan lampu
led = Pin(12, Pin.OUT)

# Menghubungkan ke WIFI
print("Menguhungkan ke WIFI", end="")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Wokwi-GUEST', '')
while not sta_if.isconnected():
  print(".", end="")
  time.sleep(0.1)
print("Terhubung!")

# Menghubungkan ke MQTT Server
try:
    print("Menghubungkan ke server MQTT... ", end="")
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print("Terhubung!")
except Exception as e:
    print(f"Gagal terhubung, kode error: {e}")
    raise SystemExit

# Fungsi untuk mengambil data dari topic aktuasi led
def ledCb(topic, msg):
    """Fungsi untuk mengambil data dari topic aktuasi led"""
    try:
        print(f"Pesan telah diterima: {msg.decode()}")
        message = ujson.loads(msg)
        if message.get('status') == 'ON':
            led.on()
            print("Led menyala")
        elif message.get('status') == 'OFF':
            led.off()
            print("Led mati")
    except Exception as e:
        print(f"Terjadi error: {e}") 

# Subscribe ke topik aktuasi led
client.set_callback(ledCb) 
client.subscribe(MQTT_SUB_TOPIC) 
print(f"Subscribe ke topic {MQTT_SUB_TOPIC}") 

# program utama untuk menentukan lampu ON atau OFF
prev_weather = ""
prev_led_status = ""
while True:
    print("Mengukur kondisi cuaca... ", end="")
    sensor.measure() 
    temperature = sensor.temperature()
    humidity = sensor.humidity()

    sensor_message = ujson.dumps({
        "temperature": temperature,
        "humidity": humidity
    })

    if sensor_message != prev_weather:
        print("Data diperbarui!")
        print(f"""
        Pesan dikirimkan ke MQTT 
        topic {MQTT_PUB_TOPIC}: 
        {sensor_message}""")
        client.publish(MQTT_PUB_TOPIC, sensor_message)
        prev_weather = sensor_message
    else:
        print("Tidak ada perubahan")
    
    led_message = lambda status: {
        'status': status
    }

    if temperature <= 20 or humidity >= 40:
        curr_led_status = led_message('ON')
    elif temperature > 20 or humidity < 40:
        curr_led_status = led_message('OFF')
    else: 
        curr_led_status = prev_led_status

    if curr_led_status != prev_led_status:
        print(f"""
        Status diperbarui
        Pesan dikirimkan ke MQTT 
        topic {MQTT_SUB_TOPIC}: 
        {curr_led_status}""")
        client.publish(MQTT_SUB_TOPIC, ujson.dumps(curr_led_status))
        prev_led_status = curr_led_status

    client.check_msg()
    time.sleep(1)


