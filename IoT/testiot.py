from board import SCL, SDA, D23     # APDS9960 lumiere, couleur, pression
from adafruit_apds9960 import *
import RPi.GPIO as GPIO
import smbus2   # BME 280
import bme280   # BME 280 temperature et humidite
import busio    # APDS9960
import digitalio    # APDS9960
import time     # APDS9960
import datetime
import mysql.connector as mysql


now_time = datetime.datetime.now()

### db mariadb connect  ###
mysql_connection = mysql.connect(database='dbplanteco', user='root', password='root')
cursor = mysql_connection.cursor()

### Capteur BME 280, Temperature / Pression / Humidité de l'air/Pression
port = 1
address = 0x77

bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)
data = bme280.sample(bus, address, calibration_params)

### Capteur APDS 9960, Couleur / Proximité / Luminosité

int_pin = digitalio.DigitalInOut(D23)
i2c = busio.I2C(SCL, SDA)
apds = APDS9960(i2c, interrupt_pin=int_pin)

apds.enable_color = True

while not apds.color_data_ready:
    time.sleep(0.005)

# Capteur sol

channel = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)


### donnees ###
r, g, b, c = apds.color_data   
temperature = data.temperature  #en degre celsius
pression = data.pressure  #en hpa
humidite_air = data.humidity #en pourcent
temperature_lumiere = colorutility.calculate_color_temperature(r, g, b) #Kelvin degrees
lumin_lux = colorutility.calculate_lux(r, g, b)
data2 = [temperature, now_time_format]



def callback(channel):
    if GPIO.input(channel):
        print("Water Detected!")
    else:
        print("Water Detected!")
 
GPIO.add_event_detect(channel, GPIO.BOTH, bouncetime=300)  # let us know when the pin goes HIGH or LOW
GPIO.add_event_callback(channel, callback)  # assign function to GPIO PIN, Run function on change
 


#print("r: {}, g: {}, b: {}, c: {}".format(r, g, b, c))

#print(temperature, humidite_air, pression, lumin_lux)

### Push db values, close db ###

cursor.execute("INSERT INTO temperature(valeur,date) VALUES(%s,%s)", (temperature, now_time))
cursor.execute("INSERT INTO lumiere(valeur,date) VALUES(%s,%s)", (temperature_lumiere, now_time))
cursor.execute("INSERT INTO humidite_air(valeur,date) VALUES(%s,%s)", (humidite_air, now_time))
#cursor.execute("INSERT INTO humidite_sol(valeur,date) VALUES(%s,%s)", (humidite, now_time))
cursor.execute("INSERT INTO pression(valeur,date) VALUES(%s,%s)", (pression, now_time))
mysql_connection.commit()
cursor.close()
mysql_connection.close()
