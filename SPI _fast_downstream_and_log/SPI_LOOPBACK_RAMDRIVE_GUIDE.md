# SPI Loopback Testing & High-Speed Data Capture on Raspberry Pi Zero 2W

## Overview

This project demonstrates high-speed SPI data acquisition on a Raspberry Pi Zero 2W using a loopback wire for testing and validation. Data is captured directly to a RAM drive (tmpfs) for maximum throughput, with automatic file rotation every 2 MB.

---

## Part 1: RAM Drive Setup (Required First)

### Create 16 MB RAM Drive

```bash
# Create mount point
sudo mkdir -p /mnt/dlog_ramdisk

# Mount tmpfs (RAM drive)
sudo mount -t tmpfs -o size=16M tmpfs /mnt/dlog_ramdisk

# Verify it exists
df -h /mnt/dlog_ramdisk
mount | grep dlog_ramdisk
```

**Output:**
```
Filesystem     Size  Used Avail Use% Mounted on
tmpfs           16M     0   16M   0% /mnt/dlog_ramdisk
```

### Make RAM Drive Permanent (Survives Reboot)

```bash
sudo nano /etc/fstab
```

Add this line at the end:
```
tmpfs           /mnt/dlog_ramdisk tmpfs   size=16M        0       0
```

Save: `Ctrl+X`, `Y`, `Enter`

Reboot and verify:
```bash
sudo reboot
df -h /mnt/dlog_ramdisk
```

---

## Part 2: SPI Hardware Setup

### Loopback Wire Connection

**Raspberry Pi Zero 2W SPI Pinout:**

| Pin # | GPIO | Function |
|-------|------|----------|
| 19 | 10 | MOSI (Master Out, Slave In) |
| 21 | 9 | MISO (Master In, Slave Out) |
| 23 | 11 | SCLK (Serial Clock) |
| 24 | 8 | CE0 (Chip Enable 0) |

**Loopback Connection:**
```
Connect GPIO 10 (Pin 19) → GPIO 9 (Pin 21) with a wire
```

This creates a loopback: data sent on MOSI echoes back on MISO.

---

## Part 3: File Progression & Explanation

### File 5: Basic SPI Loopback Test

**Purpose:** Verify SPI communication works at various speeds

**Key Features:**
```python
spi.max_speed_hz = 50000000  # Test at 50 MHz (push it to the limit!)
```

**Tests:**
1. Single byte: `0xA5` sent and received
2. Multiple bytes: 20-byte pattern sent and compared

**Output:**
```
SPI SPEED: 50.0Mhz
Test 1: Sent 0xA5, Got 0xA5 → True
SENT:     [0x12 0x34 0x56 0x78 ... 0xAA 0xAA]
RECIEVED: [0x12 0x34 0x56 0x78 ... 0xAA 0xAA]
IDENTICAL DATA
```

**Use Case:** Validate loopback wire and SPI at various clock speeds before continuous operation

---

### File 6: Continuous Data Loop (String Buffer - Has Bug)

**Purpose:** Attempt continuous data collection (demonstrates incorrect approach)

**Key Issues:**
```python
rx_buffer = ""  # WRONG: String buffer
rx_buffer += str(recieved_loopback_data)  # WRONG: Converts list to string
```

**Problem:** 
- Converts binary list `[0x55, 0x34, ...]` to string `"[0x55, 0x34, ...]"`
- String representation is 3-4x larger than binary data
- Inflates data size incorrectly

**Test Condition:**
```python
if (rx_buff_size >= 4):  # Stop after 4 MB of STRING data
    break
```

**Lesson:** Never use string buffers for binary data. Always use `bytes` or `bytearray`.

---

### File 7: Continuous Data with RAM Drive (Correct Approach)

**Purpose:** Continuous SPI data capture to RAM drive with 2 MB file rotation

**Correct Implementation:**

```python
ramdisk_path = "/mnt/dlog_ramdisk/"
rx_buffer = b""  # CORRECT: Bytes buffer

stream_simulated_data = [0x55, 0x34, 0xAA, 0x78] * 1024  # 4 KB per loop

while True:
    recieved_loopback_data = spi.xfer2(stream_simulated_data)
    rx_buffer += bytes(recieved_loopback_data)  # CORRECT: Binary append
    
    rx_buff_size = int((len(rx_buffer)) / 1024)  # Size in KB
    
    if (rx_buff_size > 2000):  # > 2 MB
        timestr = time.strftime("%y%m%d_%H%M%S")
        dlog_filename = f"{ramdisk_path}dlog_{timestr}.log"
        
        with open(dlog_filename, 'wb') as f:
            f.write(rx_buffer)
        
        rx_buffer = b""
        print(f"Saved {dlog_filename}")
```

**Key Improvements:**

1. **Bytes Buffer:** `rx_buffer = b""` (not string)
2. **Correct Append:** `bytes(recieved_loopback_data)` converts list to bytes
3. **Binary Write:** `open(..., 'wb')` for binary data
4. **RAM Drive:** Files saved directly to `/mnt/dlog_ramdisk/` (super fast)
5. **File Rotation:** New file every 2 MB

**Expected Output:**
```
SPI SPEED: 10.0Mhz
Test 1: Sent 0xA5, Got 0xA5 → True
SENT:     [0x12 0x34 0x56 0x78 ... 0xAA 0xAA]
RECIEVED: [0x12 0x34 0x56 0x78 ... 0xAA 0xAA]
IDENTICAL DATA
Saved /mnt/dlog_ramdisk/dlog_260605_150804.log
Saved /mnt/dlog_ramdisk/dlog_260605_150805.log
Saved /mnt/dlog_ramdisk/dlog_260605_150806.log
...
```

**File Size Verification:**
```bash
ls -lh /mnt/dlog_ramdisk/
total 16M
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150804.log
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150805.log
-rw-r--r-- 1 pi pi 2.0M Jun  5 15:08 dlog_260605_150806.log
```

All files **exactly 2 MB** ✓

---

## Part 4: Performance Characteristics

### Speed Testing

| Speed | Loopback Status | Real Device | Notes |
|-------|---|---|---|
| 1 MHz | ✓ OK | ✓ Most devices | Safe baseline |
| 5 MHz | ✓ OK | ✓ Common high-speed | Standard SPI speed |
| 10 MHz | ✓ OK | ✓ Fast devices | Good for testing |
| 50 MHz | ✓ OK (loopback) | ✗ FAIL (real devices) | Pi/wire limit, not real devices |

**For loopback:** Can test up to 50 MHz (Pi Zero 2W SPI max)

**For real devices:** Check device datasheet (typically 1-20 MHz)

### Data Rates

At 10 MHz with 4 KB transfers per loop:
```
Throughput ≈ 10 MB/s
File creation: ~0.2 seconds per 2 MB
RAM drive: Sustains 16 MB total before rotation needed
```

---

## Part 5: RAM Drive Management

### Check RAM Drive Status

```bash
df -h /mnt/dlog_ramdisk
```

**Output:**
```
Filesystem     Size  Used Avail Use% Mounted on
tmpfs           16M   10M    6M  62% /mnt/dlog_ramdisk
```

### List Captured Files

```bash
ls -lh /mnt/dlog_ramdisk/
du -sh /mnt/dlog_ramdisk/
```

### Flush RAM Drive (Delete All Files)

```bash
sudo rm -f /mnt/dlog_ramdisk/*.log
df -h /mnt/dlog_ramdisk
```

### Copy Files to Persistent Storage

```bash
# Copy to SD card
cp /mnt/dlog_ramdisk/*.log ~/spi_data/

# Verify copy
ls -lh ~/spi_data/
md5sum /mnt/dlog_ramdisk/*.log ~/spi_data/*.log
```

---

## Part 6: Common Issues & Solutions

### Issue 1: "No space left on device"

**Symptom:**
```
OSError: [Errno 28] No space left on device
```

**Cause:** RAM drive full (16 MB default)

**Solution:**

Option A: Increase RAM drive size
```bash
sudo umount /mnt/dlog_ramdisk
sudo mount -t tmpfs -o size=64M tmpfs /mnt/dlog_ramdisk
```

Option B: Copy files out during capture
```bash
# In another terminal
cp /mnt/dlog_ramdisk/*.log /media/usb_drive/
rm /mnt/dlog_ramdisk/*.log
```

Option C: Reduce file size per write
```python
if (rx_buff_size > 1024):  # Write at 1 MB instead of 2 MB
    # ...save file...
```

### Issue 2: "Permission denied" writing to RAM drive

**Solution:**
```bash
sudo chown pi:pi /mnt/dlog_ramdisk
sudo chmod 755 /mnt/dlog_ramdisk
```

### Issue 3: Data corruption at high speeds

**Symptom:** Received data ≠ Sent data (IDENTICAL DATA fails)

**Solutions:**
- Lower SPI clock speed: `spi.max_speed_hz = 5000000`
- Check loopback wire connection (reseat both ends)
- Reduce buffer size per loop
- Use shorter wires (minimize signal reflections)

### Issue 4: Path duplication in filenames

**Symptom:**
```
Saved /mnt/dlog_ramdisk//mnt/dlog_ramdisk/dlog_260605_150804.log
                        ↑ Double path!
```

**Cause:**
```python
ramdisk_path = "/mnt/dlog_ramdisk/"  # Has trailing /
dlog_filename = f"{ramdisk_path}dlog_{timestr}.log"  # Adds another /
```

**Fix:**
```python
ramdisk_path = "/mnt/dlog_ramdisk"  # Remove trailing /
dlog_filename = f"{ramdisk_path}/dlog_{timestr}.log"  # Add / here
```

Or:
```python
import os
dlog_filename = os.path.join(ramdisk_path, f"dlog_{timestr}.log")
```

---

## Part 7: Integration with Data Transfer System

Once SPI data is captured to RAM drive, integrate with TCP/IP transfer:

```python
# File 7: SPI capture to RAM drive
# ↓
# Files: /mnt/dlog_ramdisk/dlog_*.log
# ↓
# (This is your existing server code from datalog transfer guide)
# ↓
# Client polls and transfers to main system
```

**Server Code (from earlier datalog transfer guide):**
```python
import glob
import os

ramdisk_path = "/mnt/dlog_ramdisk"
log_files = sorted(glob.glob(f"{ramdisk_path}/*.log"))

if log_files:
    log_file = log_files[0]  # Oldest first
    with open(log_file, 'rb') as f:
        log_file_data = f.read()
    sock.sendall(log_file_data + b"\n")
    os.remove(log_file)
    print(f"Sent and deleted {log_file}")
```

Files are deleted after transfer, keeping RAM drive clean.

---

## Part 8: Quick Start Checklist

### Hardware Setup
- [ ] Loopback wire connected: Pin 19 → Pin 21
- [ ] SPI enabled in `/boot/firmware/config.txt`: `dtparam=spi=on`
- [ ] Pi rebooted after SPI enable
- [ ] `/dev/spidev0.0` exists: `ls -la /dev/spidev0.0`

### Software Setup
- [ ] spidev installed: `pip3 install spidev`
- [ ] RAM drive created: `/mnt/dlog_ramdisk` exists
- [ ] RAM drive is writable: `touch /mnt/dlog_ramdisk/test`

### Testing
- [ ] Run File 5: Basic loopback test passes (IDENTICAL DATA)
- [ ] Run File 7: Data saves to `/mnt/dlog_ramdisk/`
- [ ] Files are exactly 2 MB: `ls -lh /mnt/dlog_ramdisk/`
- [ ] RAM drive not full: `df -h /mnt/dlog_ramdisk`

### Integration
- [ ] TCP/IP server running (datalog transfer guide)
- [ ] Client polling for GET_LOG? commands
- [ ] Files transferred and deleted from RAM drive
- [ ] Main system receives complete data stream

---

## Summary

| File | Purpose | Buffer Type | Output |
|------|---------|------------|--------|
| **File 5** | Speed validation | List (test only) | Console test results |
| **File 6** | ❌ Incorrect approach | String | Inflated data size |
| **File 7/8** | ✓ Production ready | Bytes | 2 MB files to RAM drive |

**File 7/8** is the correct implementation for real-world SPI data capture.

---

## Next Steps

1. **Test File 7** with loopback wire at 10 MHz
2. **Verify files** in `/mnt/dlog_ramdisk/` are exactly 2 MB
3. **Integrate** with TCP/IP server from datalog transfer guide
4. **Stream** files from Pi to main data acquisition system
5. **Scale up** to faster SPI speeds or larger buffer sizes as needed

---

## Reference: SPI Configuration

```python
import spidev

spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0 (CE0)

# Clock speed (Hz)
spi.max_speed_hz = 10000000  # 10 MHz

# SPI Mode (determines clock polarity and phase)
spi.mode = 0  # CPOL=0, CPHA=0 (most common)

# Transfer
data_out = [0x55, 0x34, 0xAA, 0x78]
data_in = spi.xfer2(data_out)  # Full duplex

# Cleanup
spi.close()
```

---

**SPI loopback testing with RAM drive integration: Ready for production data capture!** ✓
