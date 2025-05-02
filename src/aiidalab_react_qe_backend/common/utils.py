import typing as t
import pydantic as pdt


class WithUI:
    def __init__(self, schema: dict | None = None, **ui_props: t.Any):
        self.schema = schema
        self.ui_props = ui_props


class WithLabels:
    def __init__(self, labels: list[str]):
        self.labels = labels


class WithWidget:
    def __init__(self, widget: str):
        self.widget = widget


class WithItems:
    def __init__(self, **item_schema: t.Any):
        self.item_schema = item_schema


class Patch:
    def __init__(self, field: str):
        self.field = field
        self._properties: dict[str, dict] = {}

    def set_options(self, options: list[str]) -> "Patch":
        self._properties.setdefault(self.field, {})["enum"] = options
        return self

    def set_default(self, default: t.Any) -> "Patch":
        self._properties.setdefault(self.field, {})["default"] = default
        return self

    def to_dict(self) -> dict[str, dict]:
        return {"properties": self._properties}


class Schema:
    def __init__(
        self,
        *,
        schema: dict | None = None,
        properties: list[str] | None = None,
        patches: list[Patch] | None = None,
        conditions: list["Condition"] | None = None,
    ):
        self.schema = schema
        self.properties = properties or []
        self.patches = patches or []
        self.conditions = conditions or []

        if self.schema is not None:
            if any([self.properties, self.patches, self.conditions]):
                raise ValueError(
                    "If 'schema' is provided, no other options are allowed."
                )

    def to_dict(self) -> dict:
        if self.schema:
            return self.schema

        result: dict[str, t.Any] = {}

        if self.patches:
            for patch in self.patches:
                for field, props in patch.to_dict()["properties"].items():
                    (
                        result.setdefault("properties", {})
                        .setdefault(field, {})
                        .update(props)
                    )

        if self.properties:
            for name in self.properties:
                result.setdefault("properties", {})[name] = {
                    "$ref": f"#/definitions/{name}"
                }

        if self.conditions:
            if len(self.conditions) == 1:
                result.update(self.conditions[0].to_json())
            else:
                result["allOf"] = [cond.to_json() for cond in self.conditions]

        return result


class Condition:
    def __init__(self, field: str):
        self.field = field
        self._if: dict = {}
        self._then: dict | None = None
        self._else: dict | None = None

    def is_true(self) -> "Condition":
        self._if = {"properties": {self.field: {"const": True}}}
        return self

    def is_false(self) -> "Condition":
        self._if = {"properties": {self.field: {"const": False}}}
        return self

    def equals(self, value: t.Any) -> "Condition":
        self._if = {"properties": {self.field: {"const": value}}}
        return self

    def then_(self, **kwargs) -> "Condition":
        schema = Schema(**kwargs)
        self._then = schema.to_dict()
        return self

    def else_(self, **kwargs) -> "Condition":
        schema = Schema(**kwargs)
        self._else = schema.to_dict()
        return self

    def to_json(self) -> dict:
        return {
            "if": self._if,
            "then": self._then,
            **({"else": self._else} if self._else is not None else {}),
        }


def if_(field: str) -> Condition:
    return Condition(field)


IsConditional = type("_IsConditional", (), {})()


class CustomBaseModel(pdt.BaseModel):
    __with_ui__: dict[str, t.Any] = {}
    __dependencies__: list[str] = []

    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        schema = super().model_json_schema(*args, **kwargs)
        defs: dict[str, t.Any] = schema.setdefault("definitions", {})
        props: dict[str, t.Any] = schema.get("properties", {})

        conditional_fields = {
            name
            for name, field in cls.model_fields.items()
            if any(meta is IsConditional for meta in field.metadata)
        }

        updated_props = {}
        for name, field_schema in props.items():
            model_field = cls.model_fields[name]

            for meta in model_field.metadata:
                if isinstance(meta, WithItems):
                    field_schema.setdefault("items", {}).update(meta.item_schema)

            defs[name] = field_schema

            if name not in conditional_fields:
                updated_props[name] = {"$ref": f"#/definitions/{name}"}

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
        ui_schema = {
            "ui:submitButtonOptions": {
                "norender": True,
            }
        }

        if cls.__with_ui__:
            ui_schema["ui:options"] = cls.__with_ui__

        for field_name, model_field in cls.model_fields.items():
            if not model_field.metadata:
                continue
            ui_schema[field_name] = {}
            for meta in model_field.metadata:
                # For full (flexible) ui schema support
                if isinstance(meta, WithUI):
                    if meta.schema:
                        ui_schema[field_name].update(meta.schema)
                    else:
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
