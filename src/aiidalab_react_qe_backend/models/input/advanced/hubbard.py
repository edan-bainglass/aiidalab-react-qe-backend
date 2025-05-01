import typing as t

import pydantic as pdt

from aiidalab_react_qe_backend.common.utils import CustomBaseModel, IsConditional, if_


class HubbardUSettings(CustomBaseModel):
    model_config = pdt.ConfigDict(title="Hubbard U")

    use_hubbard: t.Annotated[
        bool,
        pdt.Field(
            title="Enable U",
        ),
    ] = False
    U: t.Annotated[
        float,
        pdt.Field(
            title="U (eV)",
            ge=0.0,
        ),
        IsConditional,
    ] = 0.0

    __conditionals__ = [
        if_("use_hubbard")
        .is_true()
        .then_(
            properties=["U"],
        ),
    ]
