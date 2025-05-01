from .convergence import ConvergenceSettings
from .smearing import SmearingSettings
from .hubbard import HubbardUSettings

__all__ = [
    "ConvergenceSettings",
    "SmearingSettings",
    "HubbardUSettings",
]

ADVANCED_SETTINGS = {
    "convergence": ConvergenceSettings,
    "smearing": SmearingSettings,
    "hubbard": HubbardUSettings,
}
