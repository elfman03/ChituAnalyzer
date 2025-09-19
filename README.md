# ChituAnalyzer
Analyze protocol between Qidi X-Plus (gen1)'s Chitu board and its ESP01 interface

My Qidi X-Plus (gen1) has a Chitu board that includes an ESP01.  Unfortunately, it only speaks to Qidi's slicer or Chitu HB.  

The ESP01 OS that it runs is custom to Chitu/Qidi and has several issues:
   * Its UDP protocol and associated slicer APIs do not work well in the presence of multiple subnets (e.g., when tailscale is running)
   * It has no way to turn off access point mode which pollutes the access point infrastructure
   * It only works with the custom port 3000 UDP interface which is not supported by other slicers/tools
   * The ESP-01 cannot be replaced with another one without an authorization code from Chitu who says they no longer provide the codes.

This is a collection of scripts and info from analyzing the interface between the ESP01 and the Chitu board to try to replace it with another solution.

Analysis technique precondition:
   * Replace ESP01 in printer with an ESP running ESPEasy and a TCP bridge
       * Device 1 : Communication - Serial Server named "serial-115200" - port HW Serial0
       * Device 2 : Communication - Serial Server named "serial-2250000" - port HW Serial0
       * Rule set 1:
           ```
           On System#Boot Do
           TaskDisable serial-2250000
           TaskEnable serial-115200
           SerialSendMix,";auth ok 2",0x0d,0x0a,0x0d,0x0a,"ready",0x0d,0x0a,";CONNECT,4",0x0d,0x0a,0x0d,0x0a,"OK",0x0d,0x0a
           TaskDisable serial-115200
           TaskEnable serial-2250000
           Endon
           ```
   * Place the ESP01 from the printer into a ESP USB adapter connected to pc (windows)

Analysis technique:
   * Traffic from the printer to the ESPeasy ESP will funnel over the TCP bridge and can be monitored remotely
   * Traffic from the TCP bridge will route into the printer
       * We can thus see what the printer is trying to say to the ESP and inject responses (from a python script running remotely)
       * script: fakeesp.py
          * start the printer then start the fakeesp.py app on the PC.  It should then log the requests that are sent to the ESP from the printer and respond to them enough for the printer to report on its screens the details of the interface.  in addition, the fakeesp will fake a file listing and a file upload for testing purposes.
   * Traffic from the Chitu ESP will funnel over the USB serial interface on the PC
       * We can thus see what the Chitu proprietary ESP wants to say to the printer and inject fake responses (from a python script on the PC)
       * my USB adapter does not seem to want to work at 2250000 baud but even without the speed change it appears to respond well to traffic
       * script: fakechitu.py
          * start script, reset the chitu ESP then connect to the chitu esp from the Chitu HB app.  you should see requests go back/forth and the Chitu HB app should see what looks like a Chitu printer attached


NOTES:   interesting reference discussion regarding Chitu's command codes: https://www.reddit.com/r/resinprinting/comments/q83622/chitu_systems_boards_gcode/
