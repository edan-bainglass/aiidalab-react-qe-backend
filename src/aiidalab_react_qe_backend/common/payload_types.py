import typing as t
import pydantic as pdt


class PatchRequestPayload(pdt.BaseModel):
    requirements: dict[str, t.Any] | None = None
