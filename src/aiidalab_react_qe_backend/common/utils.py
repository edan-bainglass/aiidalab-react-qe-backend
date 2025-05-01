import typing as t
import pydantic as pdt


class WithUI:
    def __init__(self, **ui_props: t.Any):
        self.ui_props = ui_props


class WithLabels:
    def __init__(self, labels: list[str]):
        self.labels = labels


class WithWidget:
    def __init__(self, widget: str):
        self.widget = widget


class Patch:
    def __init__(self, field: str):
        self._field = field
        self._properties: dict[str, dict] = {}

    def set_options(self, options: list[str]) -> "Patch":
        self._properties.setdefault(self._field, {})["enum"] = options
        return self

    def set_default(self, default: t.Any) -> "Patch":
        self._properties.setdefault(self._field, {})["default"] = default
        return self

    def to_dict(self) -> dict:
        return {"properties": self._properties}


class Condition:
    def __init__(
        self,
        field: str,
    ):
        self.field = field
        self._if: dict = {}
        self._then: dict | Patch | Condition | None = None
        self._else: dict | Patch | Condition | None = None

    def is_true(self) -> "Condition":
        self._if = {"properties": {self.field: {"const": True}}}
        return self

    def is_false(self) -> "Condition":
        self._if = {"properties": {self.field: {"const": False}}}
        return self

    def is_equal(self, value: t.Any) -> "Condition":
        self._if = {"properties": {self.field: {"const": value}}}
        return self

    def then(
        self,
        schema: dict | None = None,
        patch: Patch | None = None,
        condition: t.Optional["Condition"] = None,
    ) -> "Condition":
        self._then = schema or patch or condition
        assert self._then is not None, "missing 'then' condition"
        return self

    def else_(
        self,
        schema: dict | None = None,
        patch: Patch | None = None,
        condition: t.Optional["Condition"] = None,
    ) -> "Condition":
        self._else = schema or patch or condition
        assert self._else is not None, "missing 'else' condition"
        return self

    def to_json(self) -> dict:
        return {
            "if": self._if,
            "then": self._convert(self._then),
            **(
                {
                    "else": self._convert(self._else),
                }
                if self._else
                else {}
            ),
        }

    def _convert(self, obj):
        if isinstance(obj, Patch):
            return obj.to_dict()
        if isinstance(obj, Condition):
            return obj.to_json()
        return obj


def if_(field: str) -> Condition:
    return Condition(field)


class CustomBaseModel(pdt.BaseModel):
    __with_ui__: dict[str, t.Any] = {}  # schema-level UI options
    __dependencies__: list[str] = []

    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        schema = super().model_json_schema(*args, **kwargs)
        defs: dict[str, t.Any] = schema.setdefault("definitions", {})
        properties: dict[str, t.Any] = schema.get("properties", {})

        updated_props = {}
        for prop_name, prop_schema in properties.items():
            defs[prop_name] = prop_schema
            updated_props[prop_name] = {"$ref": f"#/definitions/{prop_name}"}

        schema["properties"] = updated_props

        conditionals: list[Condition] | None = getattr(cls, "__conditionals__", None)
        if conditionals:
            if len(conditionals) == 1:
                schema.update(conditionals[0].to_json())
            else:
                schema["allOf"] = [cond.to_json() for cond in conditionals]

        return schema

    @classmethod
    def model_ui_schema(cls) -> dict:
        ui_schema = {}

        if cls.__with_ui__:
            ui_schema["ui:options"] = cls.__with_ui__

        for field_name, model_field in cls.model_fields.items():
            if not model_field.metadata:
                continue
            ui_schema[field_name] = {}
            for meta in model_field.metadata:
                # For full (flexible) ui schema support
                if isinstance(meta, WithUI):
                    ui_schema[field_name] = {
                        f"ui:{key}": prop for key, prop in meta.ui_props.items()
                    }
                # User-friendly API
                else:
                    if isinstance(meta, WithWidget):
                        ui_schema[field_name]["ui:widget"] = meta.widget
                    if isinstance(meta, WithLabels):
                        ui_schema[field_name]["ui:enumNames"] = meta.labels

        return ui_schema

    @classmethod
    def model_dependencies(cls) -> list[str]:
        return cls.__dependencies__

    @classmethod
    def model_full_schema(cls) -> dict:
        schema = {
            "schema": cls.model_json_schema(),
        }

        if ui_schema := cls.model_ui_schema():
            schema["ui"] = ui_schema

        if dependencies := cls.model_dependencies():
            schema["dependencies"] = dependencies

        return schema
