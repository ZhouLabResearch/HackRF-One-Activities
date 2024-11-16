from scipy.io.wavfile import write
import numpy as np

# Load the demodulated signal
signal = np.load("demodulated_signal.npy")
sample_rate = 24000  # 24 kHz

# Normalize the signal for WAV format
normalized_signal = signal / np.max(np.abs(signal))
write("noaa_signal.wav", sample_rate, (normalized_signal * 32767).astype(np.int16))

print("Saved WAV file: noaa_signal.wav")
