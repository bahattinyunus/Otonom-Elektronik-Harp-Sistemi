import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.real_sdr import RealSDR

def test_hardware():
    print("--- [Otonom-EHS] Hardware Diagnostic Tool ---")
    sdr = RealSDR()
    
    if sdr.is_active():
        print(f"SUCCESS: SDR found and active at {sdr.center_freq/1e6} MHz")
        print("Capturing test frame...")
        frame = sdr.generate_spectrum_frame()
        print(f"Capture successful. Spectral bins: {len(frame)}")
        print(f"Avg Power: {sum(frame)/len(frame):.2f} dB")
        sdr.close()
        print("Hardware test PASSED.")
    else:
        print("FAILURE: Hardware not detected or driver error.")
        print("1. Check USB connection.")
        print("2. Ensure pyrtlsdr and drivers (librtlsdr) are installed.")

if __name__ == "__main__":
    test_hardware()
