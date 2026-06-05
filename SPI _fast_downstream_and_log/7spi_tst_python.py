#!/usr/bin/env python3

import spidev
import time
# ============================================================================
# INITIALIZE SPI INTERFACE
# ============================================================================

spi = spidev.SpiDev()
# Create SPI object instance

spi.open(0, 0)
# Alternative: spi.open(0, 1) uses CE1 (GPIO 7, Pin 26)
spi.max_speed_hz = 10000000  # setting to max !!!!!!! Increase the freq till error
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

ramdisk_path = "/mnt/dlog_ramdisk/"
rx_buffer = b""  # rx_buffer is in bytes 
stream_simulated_data  = [0x55, 0x34, 0xAA, 0x78] * 1024  # One block in loop = 4KB
while True:

    recieved_loopback_data = spi.xfer2(stream_simulated_data)
    rx_buffer += bytes(recieved_loopback_data) # need str to append to data 
    rx_buff_size = int ( (len(rx_buffer)) / 1024) # in KB   
    #print(f"SPI DATA RX size {rx_buff_size} KB")
    
    if (rx_buff_size > 2000):
        
        timestr = time.strftime("%y%m%d_%H%M%S") # Convert to formatted string: yymmdd_hhmmss
        dlog_filename = f"{ramdisk_path}dlog_{timestr}.log"  
        
        with open(dlog_filename, 'wb') as f:  # append in bytes
            f.write(rx_buffer ) #in bytes         
        rx_buffer = b""
        print(f"Saved {ramdisk_path}{dlog_filename}")
   

# ============================================================================
# CLEANUP
# ============================================================================

spi.close()
print("Done!")






"""

# ============= Create 16 MB RAM drive ==================
sudo mkdir -p /mnt/ramdisk
sudo mount -t tmpfs -o size=16M tmpfs /mnt/ramdisk

# Verify it's created
df -h /mnt/ramdisk
mount | grep ramdisk

#============== Make it permament =====================
sudo nano /etc/fstab
Add this line at the end:
tmpfs           /mnt/ramdisk tmpfs   size=16M        0       0



(venv) pi@raspi:~ $ python3 7spi_tst_python.py 
SPI Loopback Test
========================================
SPI SPEED: 50.0Mhz
Test 1: Sent 0xA5, Got 0xA5 → True
SENT:     [0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0xA5 0xA5 0xAA 0xAA]
RECIEVED: [0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0xA5 0xA5 0xAA 0xAA]
INDENTICAL DATA
Saved /mnt/dlog_ramdisk//mnt/dlog_ramdisk/dlog_260605_150804.log
Saved /mnt/dlog_ramdisk//mnt/dlog_ramdisk/dlog_260605_150805.log
Saved /mnt/dlog_ramdisk//mnt/dlog_ramdisk/dlog_260605_150807.log
Saved /mnt/dlog_ramdisk//mnt/dlog_ramdisk/dlog_260605_150808.log
Saved /mnt/dlog_ramdisk//mnt/dlog_ramdisk/dlog_260605_150809.log
Saved /mnt/dlog_ramdisk//mnt/dlog_ramdisk/dlog_260605_150810.log
Saved /mnt/dlog_ramdisk//mnt/dlog_ramdisk/dlog_260605_150811.log
Saved /mnt/dlog_ramdisk//mnt/dlog_ramdisk/dlog_260605_150812.log



(venv) pi@raspi:~ $ df -h
Filesystem      Size  Used Avail Use% Mounted on
udev             74M     0   74M   0% /dev
tmpfs            84M  2.4M   81M   3% /run
/dev/mmcblk0p2   29G  2.6G   25G  10% /media/root-ro
tmpfs-root      209M  2.2M  206M   2% /media/root-rw
overlayroot     209M  2.2M  206M   2% /
tmpfs           209M     0  209M   0% /dev/shm
tmpfs           5.0M  8.0K  5.0M   1% /run/lock
tmpfs            16M   16M     0 100% /mnt/dlog_ramdisk
/dev/mmcblk0p1  510M   59M  452M  12% /boot/firmware
tmpfs            42M     0   42M   0% /run/user/1000



(venv) pi@raspi:~ $ ls -lh /mnt/dlog_ramdisk/
total 16M
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150804.log
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150805.log
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150807.log
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150808.log
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150809.log
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150810.log
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150811.log
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150812.log
-rw-r--r-- 1 pi pi 352K Jun  5 15:08 dlog_260605_150814.log
(venv) pi@raspi:~ $ 



(venv) pi@raspi:~ $ python3 7spi_tst_python.py 
SPI Loopback Test
========================================
SPI SPEED: 50.0Mhz
Test 1: Sent 0xA5, Got 0xA5 → True
SENT:     [0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0xA5 0xA5 0xAA 0xAA]
RECIEVED: [0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0x12 0x34 0x56 0x78 0xA5 0xA5 0xAA 0xAA]
INDENTICAL DATA
Traceback (most recent call last):
  File "/home/pi/7spi_tst_python.py", line 69, in <module>
    f.write(rx_buffer ) #in bytes         
    ^^^^^^^^^^^^^^^^^^^
OSError: [Errno 28] No space left on device


"""
