# System Configuration for Otonom Elektronik Harp Sistemi

# SDR / RF Parameters
SAMPLING_RATE = 2.0e6  # 2 MHz
CENTER_FREQ = 433.0e6  # 433 MHz (Example ISM Band)
FFT_SIZE = 1024

# Simulation Parameters
NOISE_FLOOR = -100  # dBm
SIGNAL_STRENGTH_MIN = -80
SIGNAL_STRENGTH_MAX = -20

# Module Flags
MODULES = {
    "detector": True,
    "classifier": True,
    "direction_finder": True,
    "denoiser": True,
    "optimizer": True
}

# UI Parameters
UI_HOST = '0.0.0.0'
UI_PORT = 5000
UPDATE_INTERVAL_MS = 100
