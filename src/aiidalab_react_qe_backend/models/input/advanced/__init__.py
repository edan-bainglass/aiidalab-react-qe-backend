from aiidalab_react_qe_backend.common.utils import CustomBaseModel

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

import typing as t

CBM = t.TypeVar("CBM", bound=CustomBaseModel)

ADVANCED_SETTINGS: dict[str, CBM] = {
    "convergence": ConvergenceSettings,
    "smearing": SmearingSettings,
    "magnetization": MagnetizationSettings,
    "hubbard": HubbardUSettings,
    "pseudos": PseudopotentialSettings,
}
