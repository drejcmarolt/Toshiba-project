import network
import socket
from time import sleep
from picozero import pico_led
import machine
from machine import Pin
import rp2
import sys
from ir_tx.Toshiba import TOSHIBA
import uasyncio as asyncio

# Windows Hotspot
#ssid (Uporabniško ime Windows Hotspot-a)
#password (Geslo Windows Hotspot-a)

# Raspberry Pi Hotspot
ssid = 'RaspberryTips-WiFi'
password = 'RPIjedober.12'


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        if rp2.bootsel_button() == 1:
            sys.exit()
        print('Waiting for connection...')
        pico_led.on()
        sleep(0.5)
        pico_led.off()
        sleep(0.5)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    pico_led.on()
    return ip

def open_socket(ip):
    address = (ip, 3012)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection
    
def webpage(temperatura, modeAC, toggle):
    
    if toggle == "ON":
        colorButton = "green"
    elif toggle == "OFF":
        colorButton = "red"
    
    style = "<style> \
               body { \
                   font-family: 'Times New Roman'; \
               } \
               #content1 { \
                   display: flex; \
                   align-items: center; \
                   gap: 100px; \
                } \
               #content2 { \
                   display: flex; \
                   align-items: center; \
                   gap: 10px; \
               } \
           </style>"
    
    html= f"""HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n
\r\n
           <!DOCTYPE html>
           <html>
           <head>
           <title>IR remote for TOSHIBA AC</title>
           {style}
           </head>
           <body>
           <header>
           <h1>IR remote for TOSHIBA AC</h1>
           </header>
           <div>
           <p>Tukaj boste lahko prizigali razlicne gumba za IR remote za TOSHIBA AC.</p>
           </div>
           <div>
           <p><b></b></p>
           <form action="./tempUp">
           <input type="submit" value="^ UP" />
           </form>
           <div id="content1">
           <form action="/control">
           <select name="temperatura" onchange="this.form.submit()">
           <option value="0" {"selected" if temperatura == 0 else ""}>_</option>
           <option value="17" {"selected" if temperatura == 17 else ""}>17 °C</option>
           <option value="18" {"selected" if temperatura == 18 else ""}>18 °C</option>
           <option value="19" {"selected" if temperatura == 19 else ""}>19 °C</option>
           <option value="20" {"selected" if temperatura == 20 else ""}>20 °C</option>
           <option value="21" {"selected" if temperatura == 21 else ""}>21 °C</option>
           <option value="22" {"selected" if temperatura == 22 else ""}>22 °C</option>
           <option value="23" {"selected" if temperatura == 23 else ""}>23 °C</option>
           <option value="24" {"selected" if temperatura == 24 else ""}>24 °C</option>
           <option value="25" {"selected" if temperatura == 25 else ""}>25 °C</option>
           <option value="26" {"selected" if temperatura == 26 else ""}>26 °C</option>
           <option value="27" {"selected" if temperatura == 27 else ""}>27 °C</option>
           <option value="28" {"selected" if temperatura == 28 else ""}>28 °C</option>
           <option value="29" {"selected" if temperatura == 29 else ""}>29 °C</option>
           <option value="30" {"selected" if temperatura == 30 else ""}>30 °C</option>
           </select>
           </form>
           <form action="./tempOnOff">
           <input type="submit" value="{toggle}" style="color: {colorButton};" />
           </form>
           </div>
           <form action="./tempDown">
           <input type="submit" value="v DOWN" />
           </form>
           <div id="content2">
           <form action="./tempAuto">
           <input type="submit" value="AUTO" />
           </form>
           <form action="./tempMode">
           <input type="submit" value="MODE" />
           </form>
           <p>Mode:</p>
           <form action="/control">
           <select name="mode" onchange="this.form.submit()">
           <option value="Auto" {"selected" if modeAC == "Auto" else ""}>Auto</option>
           <option value="Cooling" {"selected" if modeAC == "Cooling" else ""}>Cooling</option>
           <option value="Drying" {"selected" if modeAC == "Drying" else ""}>Drying</option>
           <option value="Fan mode" {"selected" if modeAC == "Fan mode" else ""}>Fan mode</option>
           </select>
           </form>
           </div>
           <p>Mode: {modeAC}</p>
           </body>
           </html>
           """
    return str(html)

def mode(uvwx):
    if len(uvwx) != 4:
        print("Error")
        return
    rezultat = 0
    s = 8
    for bit in uvwx:
        rezultat += int(bit) * s
        s >>= 1
    return rezultat

def Temp(ijkl):
    if len(ijkl) != 4:
        print("Error")
        return
    rezultat = 0
    s = 8
    for bit in ijkl:
        rezultat += int(bit) * s
        s >>= 1
    rezultat1 = rezultat + 17
    if 17 <= rezultat1 <= 30:
        return rezultat
    else:
        print("Error")
        return

def serve(connection):
    #IR_led.value(0)
    # addr
    addr = mode("0000")
    # data
    data = Temp("1000")
    temperatura = 25
    Remote_light = 1
    modeAC = "Auto"
    toggle = "ON"
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        IR_led = Pin('GP26', Pin.OUT)
        toshiba_ac = TOSHIBA(IR_led)
        
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if "temperatura=" in request:
            if (Remote_light == 1 and modeAC != "Fan mode"):
                temperature = int(request.split("temperatura=")[1].split(" ")[0])
                if (temperature != 0):
                    if addr >= 8:
                        addr = addr ^ 8
                    data = temperature - 17
                    toshiba_ac.transmit(addr, data)
                    asyncio.sleep_ms(120)
                    toshiba_ac.transmit(addr, data)
                    sleep(1)
                    temperatura = temperature
                    
        if "mode=" in request:
            if (Remote_light == 1):
                mode_AC = request.split("mode=")[1].split(" ")[0]
                if addr >= 8:
                    addr = addr ^ 8
                if mode_AC == "Cooling":
                    addr = mode("0001")
                    data = Temp("1001")
                    toshiba_ac.transmit(addr, data)
                    asyncio.sleep_ms(120)
                    toshiba_ac.transmit(addr, data)
                    sleep(1)
                    temperatura = 17 + data
                    modeAC = mode_AC
                elif mode_AC == "Drying":
                    addr = mode("0010")
                    data = Temp("0101")
                    toshiba_ac.transmit(addr, data)
                    asyncio.sleep_ms(120)
                    toshiba_ac.transmit(addr, data)
                    sleep(1)
                    temperatura = 17 + data
                    modeAC = mode_AC
                elif mode_AC == "Fan+mode":
                    addr = mode("0100")
                    toshiba_ac.transmit(addr, data)
                    asyncio.sleep_ms(120)
                    toshiba_ac.transmit(addr, data)
                    sleep(1)
                    modeAC = mode_AC.replace("+", " ")
                elif mode_AC == "Auto":
                    addr = mode("0000")
                    data = Temp("1000")
                    toshiba_ac.transmit(addr, data)
                    asyncio.sleep_ms(120)
                    toshiba_ac.transmit(addr, data)
                    sleep(1)
                    temperatura = 17 + data
                    modeAC = mode_AC
            
        if request == '/tempOnOff?':
            if (Remote_light == 0):
                temperatura = 17 + data
                Remote_light = 1
                #addr = mode("1000")
                addr = addr + 8
                toshiba_ac.transmit(addr, data)
                asyncio.sleep_ms(120)
                toshiba_ac.transmit(addr, data)
                sleep(1)
                #modeAC = "Auto"
                toggle = "ON"
            else:
                temperatura = 0
                Remote_light = 0
                #addr = mode("0111")
                toshiba_ac.transmit(7, data)
                asyncio.sleep_ms(120)
                toshiba_ac.transmit(7, data)
                sleep(1)
                toggle = "OFF"
        elif request == '/tempUp?':
            if (Remote_light == 1 and temperatura < 30 and modeAC != "Fan mode"):
                if addr >= 8:
                    addr = addr ^ 8
                #addr = mode("0000")
                toshiba_ac.transmit(addr, data + 1)
                asyncio.sleep_ms(120)
                toshiba_ac.transmit(addr, data + 1)
                sleep(1)
                temperatura = 17 + data + 1
                data += 1
        elif request == '/tempDown?':
            if (Remote_light == 1 and temperatura > 17 and modeAC != "Fan mode"):
                if addr >= 8:
                    addr = addr ^ 8
                #addr = mode("0000")
                toshiba_ac.transmit(addr, data - 1)
                asyncio.sleep_ms(120)
                toshiba_ac.transmit(addr, data - 1)
                sleep(1)
                temperatura = 17 + (data - 1)
                data -= 1
        elif request == '/tempAuto?':
            addr = mode("1000")
            data = Temp("1000")
            toshiba_ac.transmit(addr, data)
            asyncio.sleep_ms(120)
            toshiba_ac.transmit(addr, data)
            sleep(1)
            temperatura = 17 + data
            Remote_light = 1
            modeAC = "Auto"
            toggle = "ON"
            
        elif request == '/tempMode?':
            if addr >= 8:
                addr = addr ^ 8
            if (addr == 0 and Remote_light == 1):
                addr = mode("0001")
                data = Temp("1001")
                toshiba_ac.transmit(addr, data)
                asyncio.sleep_ms(120)
                toshiba_ac.transmit(addr, data)
                sleep(1)
                temperatura = 17 + data
                modeAC = "Cooling"
            elif (addr == 1 and Remote_light == 1):
                addr = mode("0010")
                data = Temp("0101")
                toshiba_ac.transmit(addr, data)
                asyncio.sleep_ms(120)
                toshiba_ac.transmit(addr, data)
                sleep(1)
                temperatura = 17 + data
                modeAC = "Drying"
            elif (addr == 2 and Remote_light == 1):
                addr = mode("0100")
                toshiba_ac.transmit(addr, data)
                asyncio.sleep_ms(120)
                toshiba_ac.transmit(addr, data)
                sleep(1)
                modeAC = "Fan mode"
            elif (addr == 4 and Remote_light == 1):
                addr = mode("0000")
                data = Temp("1000")
                toshiba_ac.transmit(addr, data)
                asyncio.sleep_ms(120)
                toshiba_ac.transmit(addr, data)
                sleep(1)
                temperatura = 17 + data
                modeAC = "Auto"
        html = webpage(temperatura, modeAC, toggle)
        client.send(html)
        client.close()
        
ip = connect()
connection = open_socket(ip)
serve(connection)
