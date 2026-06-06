# SPI + DMA on Raspberry Pi Zero 2W — Summary

## Key Finding: Kernel Handles DMA Automatically

The BCM2835 SPI kernel driver has DMA permanently assigned:

```
dma0chan2    | 3f204000.spi:tx
dma0chan3    | 3f204000.spi:rx
```

Any `ioctl(SPI_IOC_MESSAGE)` call — from C++, C, or Python — automatically uses
these DMA channels. No bare metal DMA code required.

---

## Call Stack (all languages)

```
your code                kernel                    hardware
---------                ------                    --------
ioctl(SPI_IOC_MESSAGE) → bcm2835_spi driver  →  DMA channels 2 & 3
                          sets up DMA CB           SPI FIFO
                          programs hardware         continuous clock
                          your process sleeps       transfer completes
                          wakes you when done
```

---

## Within a Single Transfer

- CS asserted at start, deasserted at end
- Clock runs **continuously** for the full transfer length
- **No gaps between bytes**
- Transfer is atomic — nothing interrupts it at the hardware level
- Your process blocks; OS can schedule other tasks during transfer

---

## Between Transfers

Delays are **non-deterministic** on a non-RT kernel:

| Source | Typical delay |
|--------|--------------|
| Kernel scheduler preemption | 10µs – 10ms |
| Interrupt latency (USB, GPU, timers) | unpredictable |
| CS deassert → reassert gap | same as above |

**Solutions if between-transfer gaps matter:**
- Combine into one large transfer (best option)
- Real-time kernel (reduces jitter to ~10–50µs worst case)
- Bare metal DMA with chained control blocks (zero gap)

---

## Python vs C++ @ 50MHz

| Transfer size | Transfer time | Python overhead | Python total | C++ total |
|--------------|--------------|-----------------|--------------|-----------|
| 4KB | 655µs | ~2ms | ~3ms | ~665µs |
| 64KB | 10.5ms | ~8ms | ~18ms | ~10.51ms |

Python overhead comes from list → C byte array conversion before ioctl,
and conversion back after.

### Use C++ when:
- 4KB transfers — Python overhead dominates (3x the transfer time)
- Rapid back-to-back transfers — Python GIL and GC stack up
- Consistent timing required — Python GC can pause unpredictably
- Processing data immediately after — C++ keeps data in cache

### Python is fine when:
- 64KB single transfers — transfer time dominates overhead
- Occasional acquisitions with processing time between them
- Throughput matters more than latency

---

## Python: xfer2 vs xfer

Always use `xfer2` for continuous transfers:

```python
spi.xfer2(data)   # CS held for entire transfer  ✓
spi.xfer(data)    # CS toggles between bytes     ✗
```

---

## spidev Buffer Limit

Default spidev max transfer size is **4096 bytes**. Increase to 64KB:

```bash
echo "options spidev bufsiz=65536" | sudo tee /etc/modprobe.d/spidev.conf
sudo reboot

# verify
cat /sys/module/spidev/parameters/bufsiz
```

BCM2835 DMA hardware max per block: **65536 bytes** (16-bit length field).
Kernel splits larger transfers into multiple DMA blocks transparently.

---

## Bottom Line

| Scenario | Recommendation |
|----------|---------------|
| Single 64KB capture | `spidev` Python or C++ — both use DMA |
| 4KB pages @ 50MHz | C++ — Python overhead too high |
| Continuous 64KB back-to-back | C++ |
| Bare metal DMA | Only if bypassing kernel entirely is required |
