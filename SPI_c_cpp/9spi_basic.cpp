// SPI Loopback Test for Raspberry Pi Zero 2W (C++)
// Loopback wire: Pin 19 (MOSI/GPIO 10) → Pin 21 (MISO/GPIO 9)

#include <stdio.h>
#include <string.h>          // memset()
#include <stdint.h>          // uint8_t, uint32_t
#include <sys/ioctl.h>       // ioctl()
#include <linux/spi/spidev.h> // SPI_IOC_MESSAGE
#include <fcntl.h>           // open(), O_RDWR
#include <unistd.h>          // close()
#include <iostream>          // C++ I/O

using namespace std;

// ============================================================================
// MAIN SPI LOOPBACK TEST
// ============================================================================

int main() {
    
    // ========================================================================
    // STEP 1: OPEN SPI DEVICE
    // ========================================================================
    
    int fd = open("/dev/spidev0.0", O_RDWR);
    // fd = file descriptor for /dev/spidev0.0 (CE0, Chip Enable 0)
    // O_RDWR = Read/Write mode
    
    if (fd < 0) {
        perror("CRITICAL: Failed to open /dev/spidev0.0");
        cout << "ERROR: Make sure SPI is enabled and /dev/spidev0.0 exists" << endl;
        return 1;
    }
    
    cout << "✓ Successfully opened /dev/spidev0.0 (fd: " << fd << ")" << endl;
    
    // ========================================================================
    // STEP 2: CONFIGURE SPI PARAMETERS
    // ========================================================================
    
    uint32_t speed_hz = 1000000;  // 1 MHz clock speed
    uint8_t mode = 0;             // SPI Mode 0 (CPOL=0, CPHA=0)
    uint8_t bits_per_word = 8;    // 8 bits per transfer
    
    cout << "SPI Configuration:" << endl;
    cout << "  Speed: " << (speed_hz / 1000000) << " MHz" << endl;
    cout << "  Mode:  " << (int)mode << endl;
    cout << "  Bits:  " << (int)bits_per_word << endl;
    
    // ========================================================================
    // STEP 3: DEFINE TEST DATA
    // ========================================================================
    
    // Test pattern 1: Single byte
    uint8_t test_byte = 0xA5;  // 10100101 in binary
    
    // Test pattern 2: Multiple bytes
    uint8_t tx_data[20] = {
        0x12, 0x34, 0x56, 0x78,
        0x12, 0x34, 0x56, 0x78,
        0x12, 0x34, 0x56, 0x78,
        0x12, 0x34, 0x56, 0x78,
        0xA5, 0xA5, 0xAA, 0xAA
    };
    
    uint8_t rx_data[20] = {0};  // Initialize to zeros
    
    cout << "\nTest Data (Hex):" << endl;
    cout << "TX: ";
    for (int i = 0; i < 20; i++) {
        printf("0x%02X ", tx_data[i]);
    }
    cout << endl;
    
    // ========================================================================
    // STEP 4: SINGLE BYTE LOOPBACK TEST
    // ========================================================================
    
    cout << "\n--- Test 1: Single Byte Loopback ---" << endl;
    
    uint8_t tx_single = test_byte;
    uint8_t rx_single = 0;
    
    struct spi_ioc_transfer tr_single;
    memset(&tr_single, 0, sizeof(tr_single));
    // memset() clears struct to prevent junk data
    
    tr_single.tx_buf = (unsigned long)&tx_single;
    tr_single.rx_buf = (unsigned long)&rx_single;
    tr_single.len = 1;
    tr_single.speed_hz = speed_hz;
    tr_single.bits_per_word = bits_per_word;
    
    if (ioctl(fd, SPI_IOC_MESSAGE(1), &tr_single) < 0) {
        perror("ERROR: Single byte transfer failed");
        close(fd);
        return 1;
    }
    
    printf("Sent:     0x%02X\n", tx_single);
    printf("Received: 0x%02X\n", rx_single);
    printf("Match:    %s\n", (tx_single == rx_single) ? "✓ TRUE" : "✗ FALSE");
    
    // ========================================================================
    // STEP 5: MULTIPLE BYTE LOOPBACK TEST
    // ========================================================================
    
    cout << "\n--- Test 2: Multiple Byte Loopback ---" << endl;
    
    struct spi_ioc_transfer tr_multi;
    memset(&tr_multi, 0, sizeof(tr_multi));
    
    tr_multi.tx_buf = (unsigned long)tx_data;
    tr_multi.rx_buf = (unsigned long)rx_data;
    tr_multi.len = 20;
    tr_multi.speed_hz = speed_hz;
    tr_multi.bits_per_word = bits_per_word;
    
    if (ioctl(fd, SPI_IOC_MESSAGE(1), &tr_multi) < 0) {
        perror("ERROR: Multi-byte transfer failed");
        close(fd);
        return 1;
    }
    
    cout << "RX: ";
    for (int i = 0; i < 20; i++) {
        printf("0x%02X ", rx_data[i]);
    }
    cout << endl;
    
    // ========================================================================
    // STEP 6: VERIFY DATA INTEGRITY
    // ========================================================================
    
    cout << "\n--- Data Integrity Check ---" << endl;
    
    bool all_match = true;
    for (int i = 0; i < 20; i++) {
        if (tx_data[i] != rx_data[i]) {
            all_match = false;
            printf("Mismatch at index %d: sent 0x%02X, got 0x%02X\n", 
                   i, tx_data[i], rx_data[i]);
        }
    }
    
    if (all_match) {
        cout << "✓ ALL BYTES MATCH - LOOPBACK OK!" << endl;
    } else {
        cout << "✗ SOME BYTES DIFFER - CHECK LOOPBACK WIRE" << endl;
    }
    
    // ========================================================================
    // STEP 7: CLEANUP
    // ========================================================================
    
    if (close(fd) < 0) {
        perror("ERROR: Failed to close device");
        return 1;
    }
    
    cout << "\n✓ Device closed successfully" << endl;
    cout << "Done!" << endl;
    
    return 0;
}

// ============================================================================
// COMPILATION & USAGE
// ============================================================================
/*

COMPILE:
  g++ -o spi_loopback spi_loopback.cpp

RUN:
  sudo ./spi_loopback

EXPECTED OUTPUT (with loopback wire connected):
  ✓ Successfully opened /dev/spidev0.0 (fd: 3)
  SPI Configuration:
    Speed: 1 MHz
    Mode:  0
    Bits:  8

  Test Data (Hex):
  TX: 0x12 0x34 0x56 0x78 ...

  --- Test 1: Single Byte Loopback ---
  Sent:     0xA5
  Received: 0xA5
  Match:    ✓ TRUE

  --- Test 2: Multiple Byte Loopback ---
  RX: 0x12 0x34 0x56 0x78 ...

  --- Data Integrity Check ---
  ✓ ALL BYTES MATCH - LOOPBACK OK!

  ✓ Device closed successfully
  Done!

============================================================================

HARDWARE SETUP:
  Raspberry Pi Zero 2W - Loopback Wire Connection
  
  Pin 19 (MOSI / GPIO 10) ──┐
                             ├─ Connect with wire
  Pin 21 (MISO / GPIO 9)  ──┘

============================================================================
*/
pi@r
