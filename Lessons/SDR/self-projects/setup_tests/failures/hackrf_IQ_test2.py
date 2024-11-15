import numpy as np
import matplotlib.pyplot as plt
from hackrf import HackRF
import time
from collections import deque

# Use a deque to store collected samples with a maximum length to avoid memory overload
MAX_SAMPLES = 1 * 10**6  # Limit to 1 million samples (reduced)
iq_data = deque(maxlen=MAX_SAMPLES)

# Callback function to handle HackRF data
def hackrf_callback(samples, hackrf_obj):
    try:
        # Convert the byte data to I/Q values and append to the deque in smaller chunks
        iq_data.extend(samples[:4096])  # Store only a limited number of samples at a time to avoid overload
    except Exception as e:
        print(f"Error in callback: {e}")

# Initialize HackRF object
hackrf = HackRF()
hackrf.sample_rate = 0.5e6  # Further reduced sample rate to 0.5 MHz to lower data rate
hackrf.center_freq = 90e6  # 90 MHz
hackrf.rx_gain = 20  # RX Gain Level

try:
    # Start HackRF reception
    print("Collecting data for 1 second...")
    hackrf.start_rx(hackrf_callback)
    time.sleep(1)  # Collect data for 1 second
except KeyboardInterrupt:
    print("Stopping HackRF...")
except Exception as e:
    print(f"Error during reception: {e}")
finally:
    hackrf.stop_rx()
    hackrf.close()

# Check if enough data was collected
if len(iq_data) == 0:
    print("No data collected. Exiting.")
else:
    # Convert the collected data to I and Q components outside of the callback
    samples = np.frombuffer(bytes(iq_data), dtype=np.int8).astype(np.float32)
    I = samples[::2]
    Q = samples[1::2]

    # Plot the I/Q values
    plt.figure(figsize=(10, 6))
    plt.plot(I, label='I Component')
    plt.plot(Q, label='Q Component')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.title('HackRF I/Q Components')
    plt.grid(True)
    plt.show()
