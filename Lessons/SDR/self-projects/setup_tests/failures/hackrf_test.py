import SoapySDR
import numpy as np
import matplotlib.pyplot as plt
from SoapySDR import *  # SOAPY_SDR constants

# Configure the HackRF device
sdr = SoapySDR.Device({"device": "hackrf"})

# Set sample rate, frequency, and gain
sample_rate = 10e6  # 10 MHz
center_freq = 100e6  # 100 MHz
sdr.setSampleRate(SOAPY_SDR_RX, 0, sample_rate)
sdr.setFrequency(SOAPY_SDR_RX, 0, center_freq)
sdr.setGain(SOAPY_SDR_RX, 0, 40)  # Adjust gain as needed

# Set up receive stream
rxStream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
sdr.activateStream(rxStream)

# Define the number of samples to capture
num_samples = 4096
buffer = np.empty(num_samples, dtype=np.complex64)

# Read samples from the SDR
sr = sdr.readStream(rxStream, [buffer], num_samples)

# Check if data was read successfully
if sr.ret == num_samples:
    # Plot the received signal
    plt.figure()
    plt.plot(np.real(buffer), label="I (Real)")
    plt.plot(np.imag(buffer), label="Q (Imaginary)")
    plt.title("Received Signal")
    plt.xlabel("Sample")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.show()

    # Perform an FFT for frequency analysis
    fft_data = np.fft.fftshift(np.fft.fft(buffer))
    freq_axis = np.fft.fftshift(np.fft.fftfreq(num_samples, 1 / sample_rate))

    plt.figure()
    plt.plot(freq_axis / 1e6, 20 * np.log10(np.abs(fft_data)))  # Convert to dB
    plt.title("Frequency Spectrum")
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Magnitude (dB)")
    plt.show()
else:
    print("Failed to capture samples.")

# Cleanup
sdr.deactivateStream(rxStream)
sdr.closeStream(rxStream)
