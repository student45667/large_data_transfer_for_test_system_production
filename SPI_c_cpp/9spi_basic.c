#include <stdio.h>
#include <string.h>          // Required for memset
#include <stdint.h>          // Required for uintptr_t
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <fcntl.h>   // Defines open() and constants like O_RDWR
#include <unistd.h>  // Defines close()

int main() {
    int fd = open("/dev/spidev0.0", O_RDWR);
    
    if (fd < 0) {
        perror("CRITICAL: Failed to open /dev/spidev0.0");
        return 1; 
    }

    printf("Successfully opened device. File Descriptor is: %d\n", fd);

   
    unsigned int speed = 1000000; // 1 MHz
    unsigned char tx[8] = {0xAA, 0xBB, 0xCC, 0xDD,0x11, 0x22, 0x33, 0x44};
    unsigned char rx[8] = {0}; // Initialize to zeroes

    // 1. Declare and fully clear the struct to prevent junk data
    struct spi_ioc_transfer tr;
    memset(&tr, 0, sizeof(tr));

    tr.tx_buf = (unsigned long)tx; // 64 bit ptr
    tr.rx_buf = (unsigned long)rx; // 64 bit ptr  
    tr.len = 8;
    tr.speed_hz = speed;
    tr.bits_per_word = 8; // Good practice to explicitly state this per transfer

    // 3. Execute the actual hardware transfer
    if (ioctl(fd, SPI_IOC_MESSAGE(1), &tr) < 0) {
        perror("Error: SPI transfer failed");
        return 1;
    }

    // 4. Print the received data
    printf("Received: 0x%02X 0x%02X 0x%02X 0x%02X\n", rx[0], rx[1], rx[2], rx[3]);
    printf("          0x%02X 0x%02X 0x%02X 0x%02X\n", rx[4], rx[5], rx[6], rx[7]);

    return 0;
}
