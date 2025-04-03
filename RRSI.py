# Programa para medir la intensidad de señal WiFi (RSSI)
# Universidad Militar Nueva Granada - Ingeniería en Telecomunicaciones
# jose.rugeles@unimilitar.edu.co

import network
import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import math

# Configuración OLED
WIDTH = 128
HEIGHT = 32
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=200000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)
   
# Configuración WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
ssid = "Redmi"
password = "12345678"

# Configuración de pines GPIO
led_avanzar = Pin(16, Pin.OUT)
led_midiendo = Pin(17, Pin.OUT)
led_wifi = Pin(19, Pin.OUT)
pulsador = Pin(18, Pin.IN, Pin.PULL_UP)

# Conexión a la red WiFi
def conectar_wifi():
    wifi.connect(ssid, password)
    while not wifi.isconnected():
        led_wifi.value(not led_wifi.value())  # Parpadeo si no hay conexión
        time.sleep(0.5)
    led_wifi.on()  # Encender LED WiFi cuando se conecta
    print("Conexión establecida!")
    print("Dirección IP:", wifi.ifconfig()[0])

conectar_wifi()

# Función para calcular la desviación estándar
def calcular_desviacion_estandar(valores):
    media = sum(valores) / len(valores)
    varianza = sum((x - media) ** 2 for x in valores) / len(valores)
    return math.sqrt(varianza)

# Bucle principal
while True:
    oled.fill(0)
    oled.text("Presione el", 2, 6)
    oled.text("pulsador", 2, 16)
    oled.show()
   
    # Esperar a que se presione el pulsador
    while pulsador.value():
        time.sleep(0.1)
   
    led_avanzar.on()  # Encender LED "Avanzar"
    time.sleep(1)  # Esperar 1 segundo antes de medir
    led_avanzar.off()
   
    rssi_values = []
    led_midiendo.on()  # Encender LED "Midiendo"
   
    # Toma 200 muestras de RSSI durante 20 segundos
    for _ in range(200):
        rssi = wifi.status('rssi')
        rssi_values.append(rssi)
        time.sleep(0.1)
   
    led_midiendo.off()  # Apagar LED "Midiendo"
   
    # Calcular promedio y desviación estándar
    rssi_average = sum(rssi_values) / len(rssi_values)
    desviacion_estandar = calcular_desviacion_estandar(rssi_values)
   
    # Mostrar resultados en OLED
    oled.fill(0)
    oled.text("RSSI Prom:", 2, 6)
    oled.text(f"{round(rssi_average, 2)} dBm", 2, 16)
    oled.text("Desv Est:", 2, 26)
    oled.text(f"{round(desviacion_estandar, 2)} dBm", 2, 36)
    oled.show()
    led_avanzar.on()
    time.sleep(5)
    led_avanzar.off()
    # Guardar datos en archivo
    with open("RSSI.txt", "a") as file:
        file.write(f"RSSI Prom: {rssi_average:.2f} dBm, Desv Est: {desviacion_estandar:.2f} dBm\n")
   
    time.sleep(2)  # Esperar antes de la siguiente medición