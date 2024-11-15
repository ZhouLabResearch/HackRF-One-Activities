try:
    import SoapySDR
    from SoapySDR import *  # SOAPY_SDR constants

    # Initialize the HackRF device
    sdr = SoapySDR.Device({"driver": "hackrf"})  # or {"device": "hackrf"}
    print("Device initialized:", sdr)

    # Set sample rate, frequency, and gain
    sample_rate = 10e6  # 10 MHz
    center_freq = 100e6  # 100 MHz
    sdr.setSampleRate(SOAPY_SDR_RX, 0, sample_rate)
    sdr.setFrequency(SOAPY_SDR_RX, 0, center_freq)
    sdr.setGain(SOAPY_SDR_RX, 0, 40)  # Adjust gain as needed

    print("Device configuration successful.")
except Exception as e:
    print("Error during device setup:", e)
