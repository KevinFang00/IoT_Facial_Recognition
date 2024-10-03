import camera
import io
import base64, json
import urequests as requests
import time, network, ntptime
from machine import Pin , PWM
import gc 

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
url = 'https://xnlfklnhd5.execute-api.us-east-1.amazonaws.com/default/img'
# connect WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect('iPhone00', '00000000')
    while not wlan.isconnected():
        pass
print('network config: ', wlan.ifconfig())
pwm = PWM(Pin(4))
pwm.freq(10)
pwm.duty(4)
# create an output pin on pin #33
p0 = Pin(33, Pin.OUT)
p0.value(0)
while True:
    # configure camera
    p0.value(1)
    camera.init()
    camera.framesize(5)
    camera.quality(20)
    camera.speffect(0)

    image_64_encode = base64.encodebytes(camera.capture())

    r = requests.post(url, data=json.dumps({"key": base64.encodebytes(camera.capture())}), headers=headers)
    print(r.text,dir(r))
    p0.value(0)
    time.sleep(2)
    gc.collect()
    camera.deinit()

   

