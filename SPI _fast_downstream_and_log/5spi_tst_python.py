#!/usr/bin/env python3
"""
SPI Loopback Test for Raspberry Pi Zero 2W
Tests SPI communication with loopback wire (Pin 19 MOSI → Pin 21 MISO)
"""

import spidev

# ============================================================================
# INITIALIZE SPI INTERFACE
# ============================================================================

spi = spidev.SpiDev()
# Create SPI object instance

spi.open(0, 0)
# open(bus, device)
# Bus 0: Only SPI bus on Pi
# Device 0: Chip Enable 0 (CE0, GPIO 8, Pin 24)
# Alternative: spi.open(0, 1) uses CE1 (GPIO 7, Pin 26)

spi.max_speed_hz = 50000000  # setting to max !!!!!!! Increase the freq till error
# Set clock speed to 1 MHz (1,000,000 Hz)
# Loopback can handle 10+ MHz; real devices limited by spec sheet
# Common speeds: 100kHz, 1MHz, 5MHz, 10MHz

spi.mode = 0
# SPI Mode determines clock polarity (CPOL) and phase (CPHA)
# Mode 0: CPOL=0, CPHA=0 (most common, default for most devices)
# Mode 1: CPOL=0, CPHA=1
# Mode 2: CPOL=1, CPHA=0
# Mode 3: CPOL=1, CPHA=1

print("SPI Loopback Test")
print("=" * 40)

print(f"SPI SPEED: {spi.max_speed_hz/1000000}Mhz")

# ============================================================================
# TEST 1: SINGLE BYTE LOOPBACK
# ============================================================================

test_byte = 0xA5
# Test pattern: 0xA5 = 10100101 in binary
# Distinctive pattern to verify bit-accurate transmission

response = spi.xfer2([test_byte])
# xfer2(data_out) - Full duplex SPI transfer (simultaneous send/receive)
# Sends [0xA5] on MOSI line, reads response from MISO line simultaneously
# Returns list of received bytes: [received_byte]
# With loopback wire, MOSI echoes to MISO, so response should be [0xA5]

print(f"Test 1: Sent 0x{test_byte:02X}, Got 0x{response[0]:02X} → {test_byte == response[0]}")
# Format: 0x{value:02X} = hexadecimal format with leading zero if < 0x10
# Example: 0xA5 = "A5" (2 hex digits)
# Comparison: test_byte == response[0]


# ============================================================================
# TEST 2: MULTIPLE BYTE SEQUENCE
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
# Send all  bytes on MOSI , compare with recieved data, display in hex

# ============================================================================
# CLEANUP
# ============================================================================

spi.close()
# Release SPI interface
# Closes /dev/spidev0.0 file handle


print("Done!")

# ============================================================================
# LOOPBACK HARDWARE SETUP
# ============================================================================
# 
# Physical wire connection required:
# 
#   Raspberry Pi GPIO Header (top view):
#   ┌─────────────────────────────┐
#   │ Pin 1  Pin 2                │
#   │ ┌──────────────────────┐    │
# 19│ │ MOSI (GPIO 10) ──┐  │ GND
#   │ │                  │  │
# 21│ │ MISO (GPIO 9) ◄──┘  │ GND  ← Connect wire here
#   │ │                  │  │
# 23│ │ SCLK (GPIO 11) ──┼──│ GND
#   │ │                  │  │
# 24│ │ CE0 (GPIO 8) ────┼──│ GND
#   │ │                  │  │
#   │ └──────────────────────┘    │
#   └─────────────────────────────┘
#
# MOSI (Pin 19) → MISO (Pin 21) = Loopback wire
# 
# Data flow:
#   Pi sends byte on MOSI → Wire carries signal → Pi reads on MISO
#   Result: Received byte = Sent byte (if no errors)
#
"""

Quick Start Checklist

 SSH into Pi Zero 2W
 Run sudo raspi-config
 Enable SPI interface
 Reboot
 Verify /dev/spidev0.0 exists
 Install spidev: sudo pip3 install spidev
 Connect loopback wire: Pin 19 to Pin 21
 Create test_spi_loopback.py script
 Run: python3 test_spi_loopback.py
 Verify all tests show Match: True
 Cleanup: spi.close()

"""