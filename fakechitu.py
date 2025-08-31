import os, sys, socket, serial
from time import sleep

myport="COM6"
ser=serial.Serial(port=myport,baudrate=115200,timeout=1,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
ser.isOpen()

def printable(s):
  ss=s.replace("\x00","\\x00")
  ss=ss.replace("\r","\\r")
  ss=ss.replace("\n","\\n")
  ss=ss.replace("\x1d","\\x1d")
  ss=ss.replace("\x83","\\x83")
  return ss;

def fetchline(killnulls):
  data=""
  lastc='Z'
  #while ser.inWaiting()>0:
  ct=0;
  while (True):
    # do it with a loop instead of no timeout so we can <control-c>
    it=b""
    while(len(it)==0):
      it=ser.read(1)
    itc=chr(list(it)[0])
    if((itc!='\0') or (not killnulls)):
      data+=itc
    #print("serin "+str(len(data))+" "+lastc+" "+itc+" ---"+data.decode('utf-8')+"---")
    if(lastc=='\r' and itc=='\n'):
      colon=data.find(":")
      # ipd lines may have extra newlines
      if(data.find("+IPD,4,")==2 and colon>=0):
        payload=data[colon+1:]
        paylen=int(data[9:colon])
        if(len(payload)==paylen+2):
          print("<<<-IPD paylen="+str(paylen)+"/"+str(len(payload))+" data="+printable(data)+" -- payload="+printable(payload))
          return data
      # empty newlines precede some datas
      elif(len(data)>2):
        print("<<< "+str(len(data))+" data="+printable(data))
        return data
    lastc=itc

def doSer():
  global ser
  #
  # open connection
  #
  #tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #tcp.settimeout(3)
  #tcp.connect(("192.168.10.245",8080))
  #
  #initialized=False
  initialized=True
  inM28=False
  esp_state=0
  while(1):
    s=fetchline(False)
    ss=printable(s)
    #print("GOT: --"+s+"--")
    skip=False
    if(not skip):
      if((esp_state==0) and (s.find(";auth ok 2\r\n")!=-1)):
        print("    ESP coming online -- auth")
        esp_state=1
      elif((esp_state==1) and (s.find("\r\nready\r\n")==-0)):
        print("    ESP coming online -- ready")
        esp_state=2
      elif((esp_state==2) and (s.find(";CONNECT,4\r\n")==-0)):
        print("    ESP coming online -- CONNECT")
        esp_state=3
        # my USB sled does not seem to like 2250000 so dont actually change
        #buf=b"AT+UART_CUR=2250000,8,1,0,0\r\n"
        #ser.write(buf)
      elif((esp_state==3) and (s.find("\r\nOK\r\n")==-0)):
        esp_state=0
        print("    ESP coming online -- Baud change accept")
        # my USB sled does not seem to like 2250000 so dont actually change
        #ser.close()
        #ser=serial.Serial(port=myport,baudrate=2250000,timeout=1,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)
        #ser.isOpen()
      elif(s.find("OK,recv")==0):
        print("    ESP ready")
      elif(s.find("OK,SEND DONE")==0):
        print("    ESP done")
      elif(s.find("\r\n+IPD,4,5:M4000")==0):
        print(">>> respond to M4000")
        buf=b"AT+CIPSEND=4,88\rok B:25/0 E1:28/0 E2:1077/0 X:0.000 Y:0.000 Z:205.850 F:0/0 D:0/0/1 I:-49493/0 L:0 T:0\r\n"
        #print("------"+buf.decode('utf-8')+"------")
        ser.write(buf)
      elif(s.find("\r\n+IPD,4,5:M4001")==0):
        print(">>> respond to M4001")
        buf=b"AT+CIPSEND=4,80\rok X:0.010511 Y:0.010611 Z:0.002500 E:0.010700 T:0/274/204/205/1 U:'UTF-8' B:1\r\n"
        #print("------"+buf.decode('utf-8')+"------")
        ser.write(buf)
      elif(s.find("\r\n+IPD,4,5:M4002")==0):
        print(">>> respond to M4002")
        buf=b"AT+CIPSEND=4,9\rok V2.31\n"
        #print("------"+buf.decode('utf-8')+"------")
        ser.write(buf)
      elif(s.find("\r\n+IPD,4,5:M4003")==0):
        print(">>> respond to M4003 [POWEROFF]")
        buf=b"AT+CIPSEND=4,8\rok C:0\r\n"
        #print("------"+buf.decode('utf-8')+"------")
        ser.write(buf)
      elif(s.find("\r\n+IPD,4,5:M4004")==0):
        print(">>> respond to M4004")
        buf=b"AT+CIPSEND=4,8\rok C:0\r\n"
        #print("------"+buf.decode('utf-8')+"------")
        ser.write(buf)
      elif(s.find("\r\n+IPD,4,5:M4006")==0):
        print(">>> respond to M4006")
        buf=b"AT+CIPSEND=4,25\rok 'Unnamed-Cube.gcode'\r\n"
        #print("------"+buf.decode('utf-8')+"------")
        ser.write(buf)
      elif(s.find(":M28 ")!=-1 and s.find("\r\n+IPD,4,")==0):
        inM28=True
        print(">>> respond to M28: --"+ss+"--")
        buf=b"AT+CIPSEND=4,8\rok N:0\r\n"
        ser.write(buf)
      elif(inM28==True and s.find("\r\n+IPD,4,")==0):
        ss=printable(s)
        print("upload payload "+str(len(s))+": -----"+ss+"-----")
        buf=b"AT+CIPSEND=4,4\rok\r\n"
        ser.write(buf)
      elif(s.find("\r\n+IPD,4,6:M20 ''")==0):
        print("respond to M20")
        buf=b"AT+CIPSEND=4,17\rBegin file list\r\n"
        ser.write(buf)
        sleep(0.01)
        buf=b"AT+CIPSEND=4,16\rshorty.gcode 0\r\n"
        ser.write(buf)
        sleep(0.01)
        buf=b"AT+CIPSEND=4,15\rEnd file list\r\n"
        ser.write(buf)
        sleep(0.01)
        buf=b"AT+CIPSEND=4,8\rok L:1\r\n"
        ser.write(buf)
        #print("------"+buf.decode('utf-8')+"------")
      else:
        print("Unknown ESP packet "+str(len(s))+": \n-----"+ss+"-----")
    else:
        print("Nothing from ESP!")


doSer()
