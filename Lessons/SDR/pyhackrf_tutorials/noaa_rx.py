from python_hackrf import pyhackrf
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import os
import time

# Settings for the HackRF
record_time = 60  # Record time in seconds for a complete satellite pass
center_freq = 137.1e6  # NOAA 19 APT signal frequency
sample_rate = 2e6  # Increased sample rate for higher resolution
baseband_filter = 200e3  # Bandwidth for NOAA signals
lna_gain = 24  # Moderate gain
vga_gain = 16  # Moderate gain
output_file = "./satellite_data.raw"  # Save raw IQ data in the current folder
demodulated_file = "./demodulated_signal.npy"  # Save demodulated signal in the current folder

# Initialize HackRF
pyhackrf.pyhackrf_init()
sdr = pyhackrf.pyhackrf_open()

# Configure HackRF
allowed_baseband_filter = pyhackrf.pyhackrf_compute_baseband_filter_bw_round_down_lt(baseband_filter)
sdr.pyhackrf_set_sample_rate(sample_rate)
sdr.pyhackrf_set_baseband_filter_bandwidth(allowed_baseband_filter)
sdr.pyhackrf_set_antenna_enable(True)
sdr.pyhackrf_set_freq(center_freq)
sdr.pyhackrf_set_amp_enable(False)
sdr.pyhackrf_set_lna_gain(lna_gain)
sdr.pyhackrf_set_vga_gain(vga_gain)

print("Ensure input signals are below -5 dBm to prevent device damage.")

# Buffer for samples
samples = np.zeros(int(sample_rate * record_time), dtype=np.complex64)
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
print(f"Receiving data from {center_freq / 1e6} MHz for {record_time} seconds...")
try:
    time.sleep(record_time)
except KeyboardInterrupt:
    print("Interrupted by user")

# Stop and close HackRF
stop_flag = True
sdr.pyhackrf_stop_rx()
sdr.pyhackrf_close()
pyhackrf.pyhackrf_exit()

# Save raw IQ samples to a file
samples = samples[:last_idx]  # Trim unused samples
samples.tofile(output_file)
print(f"Saved raw IQ data to {output_file}")

# Process the data for demodulation
print("Processing received data...")
fm_demod = np.angle(samples[1:] * np.conj(samples[:-1]))  # FM demodulation

# Extract the APT subcarriers
apt_carrier = 2400
lowpass_filter = scipy.signal.firwin(101, [1100, 3700], fs=sample_rate, pass_zero=False)
filtered_signal = scipy.signal.lfilter(lowpass_filter, [1.0], fm_demod)

# Decimate the signal to match the audio bandwidth
decimation_factor = int(sample_rate / 24000)  # Down to 24 kHz
demodulated_signal = filtered_signal[::decimation_factor]

# Save demodulated data for APT image processing
np.save(demodulated_file, demodulated_signal)
print(f"Saved demodulated signal to {demodulated_file}")

# Frequency Spectrum Analysis
print("Performing frequency spectrum analysis...")
fft_result = np.fft.fftshift(np.fft.fft(demodulated_signal))
fft_power = 20 * np.log10(np.abs(fft_result) + np.finfo(float).eps)  # Convert to dB
freq_axis = np.fft.fftshift(np.fft.fftfreq(len(demodulated_signal), d=1/24000))

# Plot the frequency spectrum
plt.figure(figsize=(10, 6))
plt.plot(freq_axis, fft_power, label="Spectrum")
plt.title("Frequency Spectrum of the Demodulated APT Signal")
plt.xlabel("Frequency [Hz]")
plt.ylabel("Power [dB]")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.tight_layout()
plt.legend()
plt.show()
