from python_hackrf import pyhackrf
import numpy as np
import matplotlib.pyplot as plt
import time

## Settings for the HackRF
record_time = 5  # seconds
center_freq = 137.1e6  # Hz
sample_rate = 1e6
baseband_filter = 200e3
lna_gain = 24  # 0 to 40 dB in 8 dB steps
vga_gain = 16  # 0 to 62 dB in 2 dB steps

# Initialize HackRF
pyhackrf.pyhackrf_init()
sdr = pyhackrf.pyhackrf_open()

# Calculate the supported bandwidth relative to the desired one
allowed_baseband_filter = pyhackrf.pyhackrf_compute_baseband_filter_bw_round_down_lt(baseband_filter)

# Set up the HackRF parameters
sdr.pyhackrf_set_sample_rate(sample_rate)
sdr.pyhackrf_set_baseband_filter_bandwidth(allowed_baseband_filter)
sdr.pyhackrf_set_antenna_enable(True)
sdr.pyhackrf_set_freq(center_freq)
sdr.pyhackrf_set_amp_enable(False)
sdr.pyhackrf_set_lna_gain(lna_gain)
sdr.pyhackrf_set_vga_gain(vga_gain)

# Allocate buffer for samples
num_samples = int(sample_rate * record_time)
samples = np.zeros(num_samples, dtype=np.complex64)
last_idx = 0
stop_flag = False

# Callback function
def rx_callback(device, buffer, buffer_length, valid_length):
    global samples, last_idx, stop_flag
    if stop_flag:
        return 0
    try:
        incoming_samples = np.frombuffer(buffer, dtype=np.int8, count=valid_length)
        incoming_samples = incoming_samples[0::2] + 1j * incoming_samples[1::2]
        incoming_samples /= 128.0  # Normalize to -1 to 1

        # Add samples to the buffer
        remaining_space = len(samples) - last_idx
        to_copy = min(len(incoming_samples), remaining_space)
        samples[last_idx:last_idx + to_copy] = incoming_samples[:to_copy]
        last_idx += to_copy
    except Exception as e:
        print(f"Error in callback: {e}")
    return 0

# Start receiving
sdr.set_rx_callback(rx_callback)
sdr.pyhackrf_start_rx()

# Wait for the recording to complete
try:
    time.sleep(record_time)
except KeyboardInterrupt:
    print("Interrupted by user")

# Stop and close HackRF
stop_flag = True
sdr.pyhackrf_stop_rx()
sdr.pyhackrf_close()

# Process collected data
collected_samples = samples[:last_idx]

# Plot the collected IQ data
plt.figure(figsize=(10, 4))
plt.plot(np.real(collected_samples[:1000]), label="Real")
plt.plot(np.imag(collected_samples[:1000]), label="Imaginary")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.title("Collected IQ Samples")
plt.legend()
plt.tight_layout()
plt.show()

# Perform FFT and create the frequency axis
fft_result = np.fft.fftshift(np.fft.fft(collected_samples))
fft_power = 20 * np.log10(np.abs(fft_result) + np.finfo(float).eps)  # Convert to dB

# Generate the frequency axis in Hz
freq_axis = np.fft.fftshift(np.fft.fftfreq(len(collected_samples), d=1/sample_rate))
freq_axis = freq_axis + center_freq  # Shift to align with the center frequency

# Plot the frequency spectrum
plt.figure(figsize=(10, 4))
plt.plot(freq_axis / 1e6, fft_power)  # Convert frequency to MHz
plt.title("Frequency Spectrum")
plt.xlabel("Frequency [MHz]")
plt.ylabel("Power [dB]")
plt.grid(True)
plt.tight_layout()
plt.show()

# Clean up
pyhackrf.pyhackrf_exit()
