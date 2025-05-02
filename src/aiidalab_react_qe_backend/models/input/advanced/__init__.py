from .convergence import ConvergenceSettings
from .hubbard import HubbardUSettings
from .magnetization import MagnetizationSettings
from .pseudos import PseudopotentialSettings
from .smearing import SmearingSettings

__all__ = [
    "ConvergenceSettings",
    "HubbardUSettings",
    "MagnetizationSettings",
    "PseudopotentialSettings",
    "SmearingSettings",
]

ADVANCED_SETTINGS = {
    "convergence": ConvergenceSettings,
    "smearing": SmearingSettings,
    "magnetization": MagnetizationSettings,
    "hubbard": HubbardUSettings,
    "pseudos": PseudopotentialSettings,
}
