import typing as t

import pydantic as pdt

from aiidalab_react_qe_backend.common.utils import (
    CustomBaseModel,
    Patch,
    if_,
)


class ConvergenceSettings(CustomBaseModel):
    model_config = pdt.ConfigDict(title="Convergence")

    scfConvEng: t.Annotated[
        float,
        pdt.Field(
            title="SCF energy (Ry/atom)",
        ),
    ]
    ionicConvEng: t.Annotated[
        float,
        pdt.Field(
            title="Ionic energy (Ry/atom)",
        ),
    ]
    ionicConvForce: t.Annotated[
        float,
        pdt.Field(
            title="Ionic force (Ry/Bohr)",
        ),
    ]

    __dependencies__ = ["basic.protocol"]

    __conditionals__ = [
        if_("protocol")
        .equals("fast")
        .then_(
            patches=[
                Patch("scfConvEng").set_default(4e-10),
                Patch("ionicConvEng").set_default(1e-4),
                Patch("ionicConvForce").set_default(1e-3),
            ]
        )
        .else_(
            conditions=[
                if_("protocol")
                .equals("balanced")
                .then_(
                    patches=[
                        Patch("scfConvEng").set_default(2e-10),
                        Patch("ionicConvEng").set_default(1e-5),
                        Patch("ionicConvForce").set_default(1e-4),
                    ]
                )
                .else_(
                    patches=[
                        Patch("scfConvEng").set_default(1e-10),
                        Patch("ionicConvEng").set_default(5e-6),
                        Patch("ionicConvForce").set_default(5e-5),
                    ]
                )
            ]
        )
    ]
