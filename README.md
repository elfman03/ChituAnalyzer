# ChituAnalyzer
Analyze protocol between Qidi X-Plus (gen1)'s Chitu board and its ESP01 interface

My Qidi X-Plus (gen1) has a Chitu board that includes an ESP01.  Unfortunately, it only speaks to Qidi's slicer or Chitu HB.  

The ESP01 OS that it runs is custom to Chitu/Qidi and has several issues:
   * Its UDP protocol and associated slicer APIs do not work well in the presence of multiple subnets (e.g., when tailscale is running)
   * It has no way to turn off access point mode which pollutes the access point infrastructure
   * It only works with the custom port 3000 UDP interface which is not supported by other slicers/tools
   * The ESP-01 cannot be replaced with another one without an authorization code from Chitu who says they no longer provide the codes.

This is a collection of scripts and info from analyzing the interface between the ESP01 and the Chitu board to try to replace it with another solution.
