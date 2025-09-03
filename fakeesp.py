import os, sys, socket
from time import sleep
 
def printable(s):
  ss=s.replace("\x00","\\x00")
  ss=ss.replace("\r","\\r")
  ss=ss.replace("\n","\\n")
  ss=ss.replace("\x1d","\\x1d")
  ss=ss.replace("\x83","\\x83")
  return ss;

def doTcp():
  #
  # open connection
  #
  tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  tcp.settimeout(3)
  tcp.connect(("192.168.10.245",8080))
  #
  initialized=0
  #initialized=1
  while(1):
    skip=False
    data=b""
    try:
      data=tcp.recv(2048)
    except:
      skip=True
    if(not skip):
      s=data.decode('utf-8')
      print(">>> "+printable(s))
      if(s=="AT+CIFSR\r\n"):
        print("respond to AT+CIFSR")
        buf=b'+CIFSR:APIP,"192.168.4.1"\r\n+CIFSR:APMAC,"8e:aa:b5:d5:f5:f1"\r\n+CIFSR:STAIP,"192.168.10.245"\r\n+CIFSR:STAMAC,"8c:aa:b5:d5:f5:f1"\r\n\r\nOK\r\n'
        print("------"+printable(buf.decode('utf-8'))+"------")
        tcp.send(buf)
      elif(s=="AT+CWSAP?\r\n"):
        print("respond to AT+CWSAP?")
        buf=b'+CWSAP:"3dprinter-D5F5F1-","",1,0\r\r\n\r\r\nOK\r\r\n'
        print("------"+printable(buf.decode('utf-8'))+"------")
        tcp.send(buf)
      elif(s=="AT+GMR\r\n"):
        print("respond to AT+GMR")
        # rule seems to be that the version has to start with V and can have up to 8 additional characters with \r\n added or 9 with just \n
        #y buf=b'+GMR:00,00,00,00,00,00,00,00 V10.0.12\r\nOK\r\n'
        #y buf=b'+GMR:00,00,00,00,00,00,00,00 V3.0.ab\r\nOK\r\n'
        #n buf=b'+GMR:00,00,00,00,00,00,00,00 3.0.ab\r\nOK\r\n'
        #y buf=b'+GMR:00,00,00,00,00,00,00,00 V3.0.abc\r\nOK\r\n'
        #y buf=b'+GMR:00,00,00,00,00,00,00,00 V3.0.abcd\r\nOK\r\n'
        #y buf=b'+GMR:00,00,00,00,00,00,00,00 V3.0.abcd\r\nOK\r\n'
        #n buf=b'+GMR:00,00,00,00,00,00,00,00 V3.10.abcd\r\nOK\r\n'
        #y buf=b'+GMR:00,00,00,00,00,00,00,00 V3.10.abc\r\nOK\r\n'
        #y buf=b'+GMR:00,00,00,00,00,00,00,00 V3x10abcd\r\nOK\r\n'
        #y buf=b'+GMR:00,00,00,00,00,00,00,00 Vabcdefgh\r\nOK\r\n'
        #n buf=b'+GMR:00,00,00,00,00,00,00,00 Xabcdefgh\r\nOK\r\n'
        buf=b'+GMR:00,00,00,00,00,00,00,00 Vabcdefghi\n\r\nOK\r\n'
        print("------"+printable(buf.decode('utf-8'))+"------")
        tcp.send(buf)
        #if(initialized==0):
        #  initialized=1
      elif(s=="AT+CWJAP?\r\n"):
        print("respond to AT+CWJAP?")
        buf=b'+CWJAP:"elford_iot"\r\r\n\r\r\nOK\r\r\n'
        print("------"+printable(buf.decode('utf-8'))+"------")
        tcp.send(buf)
        if(initialized==0):
          initialized=1
      elif(s.find("AT+CIPSEND=")==0):
        print("    CIPSEND: -----"+printable(s)+"-----")
        tcp.send(b"OK,SEND DONE\r\n")

      else:
        print("Unknown Chitu packet: \n-----"+printable(s)+"-----")
    else:
        print("Nothing from printer!")
        if(initialized==1):
          #buf=b'\r\n+IPD,4,5:M4000\r\nOK,recv\r\n'
          #buf=b'\r\n+IPD,4,5:M4002\r\nOK,recv\r\n'
          #buf=b'\r\n+IPD,4,5:M4006\r\nOK,recv\r\n'
          #buf=b'\r\n+IPD,4,6:M20 \'\'\r\nOK,recv\r\n'
          print("   M28")
          buf=b'\r\n+IPD,4,18:M28 shorty.gcode\r\n\r\nOK,recv\r\n'
          tcp.send(buf)
          initialized=2
        elif(initialized==2):
          print("    file packet")
          buf=b'\r\n+IPD,4,12:; hi\r\n\x00\x00\x00\x00\x1d\x83\r\nOK,recv\r\n'
          # if wrong checksum get:
          # AT+CIPSEND=4,29\rresend 0,check_sum error:-1\r\n
          tcp.send(buf)
          initialized=3
        elif(initialized==3):
          print("    send M29")
          buf=b'\r\n+IPD,4,3:M29\r\nOK,recv\r\n'
          tcp.send(buf)
          initialized=4
        elif(initialized==4):
          print("    send M20")
          buf=b'\r\n+IPD,4,6:M20 \'\'\r\nOK,recv\r\n'
          tcp.send(buf)
          initialized=100
        #print("------"+buf.decode('utf-8')+"-------")

doTcp()
