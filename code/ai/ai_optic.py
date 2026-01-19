
'''
repo : https://github.com/openmarmot/twe
email : andrew@openmarmot.com
notes : optic
'''

#import built in modules

#import custom packages

class AIOptic():
    def __init__(self, owner):
        """
        - name: string
        - magnification: float (e.g. 2.5, 4.0)
        - field_of_view: float in degrees (wider = faster acquisition at close range, if you add that later)
        - optical_quality: float (1.0 = average WWII, >1.0 = Zeiss-level clarity/coatings, <1.0 = inferior)
        - close_range_penalty: float degrees of extra angular error at very close range (<300m) for high-mag optics
            (optional realism: high-mag sights can feel "tunneled" up close)
        """
        self.owner=owner
        self.magnification = 0
        self.field_of_view = 0
        self.optical_quality = 0
        self.close_range_penalty = 0

    #---------------------------------------------------------------------------
    def get_effective_power(self):
        """Higher = better long-range precision (combines mag + quality)"""
        return self.magnification * self.optical_quality

    #---------------------------------------------------------------------------
    def get_dispersion_multiplier(self, distance):
        """Optics primarily help at longer ranges. Returns a multiplier <1.0 for good optics."""
        if distance < 500:
            # Close range: high-mag optics can slightly hurt due to narrow FOV/tunnel vision
            return 1.0 + (self.close_range_penalty * (4.0 / max(1.0, self.magnification)))
        
        # Long range: scale reduction by effective power (tune the 3.0 denominator for balance)
        effective_power = self.get_effective_power()
        return max(0.5, 3.0 / effective_power)  # Good optics (eff ~3.5+) get ~0.85x or better


    #---------------------------------------------------------------------------
