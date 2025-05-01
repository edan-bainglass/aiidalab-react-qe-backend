import typing as t

import pydantic as pdt

from aiidalab_react_qe_backend.common.utils import CustomBaseModel, WithLabels


class SmearingSettings(CustomBaseModel):
    model_config = pdt.ConfigDict(title="Smearing")

    method: t.Annotated[
        t.Literal[
            "gaussian",
            "methfessel-paxton",
            "fermi-dirac",
        ],
        pdt.Field(
            title="Method",
        ),
        WithLabels(
            [
                "Gaussian",
                "Methfessel-Paxton",
                "Fermi-Dirac",
            ]
        ),
    ] = "gaussian"
    width: t.Annotated[
        float,
        pdt.Field(
            title="Width (Ry)",
        ),
    ] = 0.05
