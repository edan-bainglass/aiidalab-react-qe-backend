from .convergence import ConvergenceSettings
from .smearing import SmearingSettings
from .hubbard import HubbardUSettings
from .pseudos import PseudopotentialSettings

__all__ = [
    "ConvergenceSettings",
    "SmearingSettings",
    "HubbardUSettings",
    "PseudopotentialSettings",
]

ADVANCED_SETTINGS = {
    "convergence": ConvergenceSettings,
    "smearing": SmearingSettings,
    "hubbard": HubbardUSettings,
    "pseudos": PseudopotentialSettings,
}
