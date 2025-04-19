import datetime
import typing as t

import pydantic as pdt


class Test2Input(pdt.BaseModel):
    model_config = pdt.ConfigDict(
        title="Second test plugin",
    )
    some_string: t.Annotated[
        str,
        pdt.Field(
            title="Text",
            default="Hello world",
        ),
    ]
    some_email: t.Annotated[
        pdt.EmailStr,
        pdt.Field(
            title="Email",
            default="my.email@fakemail.com",
        ),
    ]
    some_boolean: t.Annotated[
        pdt.StrictBool,
        pdt.Field(
            title="Bool",
            default=True,
        ),
    ]
    some_date: t.Annotated[
        datetime.date,
        pdt.Field(
            title="Date",
            default=datetime.date.today(),
        ),
    ]


def get_plugin() -> dict[str, t.Any]:
    return {
        "id": "test2",
        "label": "Second property",
        "input": {
            "schema": Test2Input.model_json_schema(),
            "ui": {
                "some_string": {
                    "ui:placeholder": "Enter some text",
                },
                "some_email": {
                    "ui:placeholder": "username@domain.com",
                },
            },
        },
    }
