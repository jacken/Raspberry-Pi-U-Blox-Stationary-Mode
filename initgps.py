#!/usr/bin/env python3
#
# Horrible hack just to get a Raspberry Pi with a HAB Supplies Raspberry Pi+ GPS Expansion Board
# into stationary mode, and to turn of uneccesary NMEA messages, not related to NTP Server timkeeping
#
# Cobbled together by Jack Zimmermann http://www.jackenhack.com


import serial


def UBXChecksum(payload):
  """Creates a checksum of the payload and returns it"""
  CK_A = CK_B = 0
  for b in payload[2:]:       # Ignore first sync bytes of command string
    CK_A += b
    CK_B += CK_A
  return CK_A & 0xff, CK_B & 0xff
    
def sendUBXCommand(ser, payload):
  """Adds checksum to payload command and sends it to the serial port. Returns true if message received."""
  # First, lets create the checksum and add it to the end
  CK_A = CK_B = 0
  for b in payload[2:]:       # Ignore first sync bytes of command string
    CK_A += b
    CK_B += CK_A
  payload.append(CK_A & 0xff)
  payload.append(CK_B & 0xff)
  ser.reset_output_buffer()
  written = ser.write(payload)
  print str(written) + " bytes written...\n"
  AkorNak = ser.read(10)
  print('{}'.format(AkorNak))
  print(''.join('{:02x}'.format(a) for a in payload))

def main():
  ser = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    write_timeout=1,
    xonxoff=False,
    rtscts=False,
    dsrdtr=False
    )


  # Put U-blox Neo M8Q GPS in stationary mode
  stationaryCmd = [0xB5, 0x62, 0x06, 0x24, 0x24, 0x00, 0x05, 0x00, 0x02, 0x03, 0x00, 0x00, 0x00, 0x00, 0x10, 0x27, 0x00, 0x00, 0x05, 0x00, 0xFA, 0x00, 0xFA, 0x00, 0x64, 0x00, 0x2C, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
  # Turn off NMEA GLL messages
  offGLL = [0xB5, 0x62, 0x06, 0x01, 0x08, 0x00, 0xF0, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01]
  # Turn off NMEA GSA messages
  offGSA = [0xB5, 0x62, 0x06, 0x01, 0x08, 0x00, 0xF0, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01]
  # Turn off NMEA GSV messages
  offGSV = [0xB5, 0x62, 0x06, 0x01, 0x08, 0x00, 0xF0, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0]
  # Turn off NMEA VTG messages
  offVTG = [0xB5, 0x62, 0x06, 0x01, 0x08, 0x00, 0xF0, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
  payload = bytearray(offGSV) # Convert to a bytearray
  sendUBXCommand(ser, payload)
  payload = bytearray(offGSA) # Convert to a bytearray
  sendUBXCommand(ser, payload)
  payload = bytearray(offGLL) # Convert to a bytearray
  sendUBXCommand(ser, payload)
  payload = bytearray(offVTG) # Convert to a bytearray
  sendUBXCommand(ser, payload)
  payload = bytearray(stationaryCmd) # Convert to a bytearray
  sendUBXCommand(ser, payload)
  
  ser.close()
if __name__ == '__main__':
    main()
