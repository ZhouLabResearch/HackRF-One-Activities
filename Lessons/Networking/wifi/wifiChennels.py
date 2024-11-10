import numpy as np
import SoapySDR
from SoapySDR import *  # Import SoapySDR API
import time

# Initialize SoapySDR HackRF device using the exact device string
sdr = SoapySDR.Device("driver=hackrf")  # Explicitly specify driver

sdr.setSampleRate(SOAPY_SDR_RX, 0, 5e6)  # Set sample rate to 5 MHz
sdr.setFrequency(SOAPY_SDR_RX, 0, 2.412e9)  # Set frequency to 2.412 GHz (Wi-Fi Channel 1)

# Set up stream for receiving
rxStream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
sdr.activateStream(rxStream)

# Buffer to store samples
num_samples = 1024
buff = np.array([0]*num_samples, np.complex64)

try:
    for _ in range(10):  # Adjust the loop to control the duration
        sr = sdr.readStream(rxStream, [buff], num_samples)
        if sr.ret > 0:
            power = np.mean(np.abs(buff) ** 2)
            print(f"Power: {10 * np.log10(power)} dB")
        time.sleep(0.5)  # Adjust delay between readings
except Exception as e:
    print("Error:", e)
finally:
    sdr.deactivateStream(rxStream)
    sdr.closeStream(rxStream)
