#!/usr/bin/env python3

import spidev

# ============================================================================
# INITIALIZE SPI INTERFACE
# ============================================================================

spi = spidev.SpiDev()
# Create SPI object instance

spi.open(0, 0)
# Alternative: spi.open(0, 1) uses CE1 (GPIO 7, Pin 26)
spi.max_speed_hz = 50000000  # setting to max !!!!!!! Increase the freq till error
spi.mode = 0

print("SPI Loopback Test")
print("=" * 40)

print(f"SPI SPEED: {spi.max_speed_hz/1000000}Mhz")

# ============================================================================
# TEST 1: SINGLE BYTE LOOPBACK
# ============================================================================

test_byte = 0xA5
response = spi.xfer2([test_byte])
print(f"Test 1: Sent 0x{test_byte:02X}, Got 0x{response[0]:02X} → {test_byte == response[0]}")

# ============================================================================
# TEST 2: DATA INTEGRITY CHK
# ============================================================================

test_data = [0x12, 0x34, 0x56, 0x78,0x12, 0x34, 0x56, 0x78,0x12, 0x34, 0x56, 0x78,0x12, 0x34, 0x56, 0x78 , 0xA5 ,  0xA5 , 0xAA,  0xAA ]
hex_str1 = ' '.join(f'0x{b:02X}' for b in test_data)
print(f"SENT:     [{hex_str1}]")

response = spi.xfer2(test_data)
hex_str2 = ' '.join(f'0x{b:02X}' for b in response)
print(f"RECIEVED: [{hex_str2}]")

if (hex_str2 == hex_str1):
    print(f"INDENTICAL DATA")
else:
    print(f"DATA ERROR")



# ============================================================================
# CONTIUS DATA LOOP
# ============================================================================
rx_buffer = ""
while True:
    stream_simulated_data  = [0x55, 0x34, 0xAA, 0x78] * 1024  # One block in loop = 4KB
    recieved_loopback_data = spi.xfer2(stream_simulated_data)
    rx_buffer += str(recieved_loopback_data) # need str to append to data 
    rx_buff_size = int ( (len(rx_buffer)) / (1024*1024)) # in MB
    print(f"SPI DATA RX size {rx_buff_size} MB")
    if (rx_buff_size >= 4):
        break

# ============================================================================
# CLEANUP
# ============================================================================

spi.close()
print("Done!")
