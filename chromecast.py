''' Functions to manipulate Chromecast. '''
import pychromecast
import sys
from logger import log

class DryRunChromecast:
    """A mock Chromecast class for dry-run mode that logs actions instead of performing them"""
    
    def __init__(self, name="DryRun"):
        self.name = name
        self.is_muted = False
        log.info(f"Using dry-run mode with mock Chromecast: {name}")
    
    def set_volume_muted(self, muted):
        previous = self.is_muted
        self.is_muted = muted
        log.info(f"[DRY-RUN] {'Muting' if muted else 'Unmuting'} Chromecast (was {'muted' if previous else 'unmuted'})")

def get_chromecast(name):
    """
    Find and return a Chromecast device by name.
    
    Args:
        name (str): Name of the Chromecast device to find
        
    Returns:
        pychromecast.Chromecast: The found Chromecast device
    """
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[name])
    
    if not chromecasts:
        print(f"No Chromecast with name '{name}' found.")
        sys.exit(1)
    
    cast = chromecasts[0]
    cast.wait()
    
    return cast

# Optional: if this file is run directly, you can include a demo function
if __name__ == "__main__":
    if len(sys.argv) > 1:
        device_name = sys.argv[1]
    else:
        device_name = "Chromecast"  # Default name
        
    cast = get_chromecast(device_name)
    print(f"Connected to {cast.device.friendly_name}")
