from abc import ABC, abstractmethod

class SDRInterface(ABC):
    """Abstract Base Class for Radio Hardware.
    
    Provides a common interface for both simulated environments 
    and real SDR hardware (USRP, HackRF, RTL-SDR).
    """

    @property
    @abstractmethod
    def fs(self) -> float:
        """Sampling rate in Hz."""
        ...

    @property
    @abstractmethod
    def center_freq(self) -> float:
        """Center frequency in Hz."""
        ...

    @property
    @abstractmethod
    def fft_size(self) -> int:
        """FFT size for PSD generation."""
        ...

    @abstractmethod
    def generate_spectrum_frame(self) -> list:
        """Returns the latest PSD frame as a list of dB values."""
        ...

    @abstractmethod
    def set_jamming(self, action: str):
        """Sets the jamming/EA mission state."""
        ...

    @abstractmethod
    def is_active(self) -> bool:
        """Returns True if the hardware/source is actively providing data."""
        ...
