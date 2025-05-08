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


class DependsOn:
    def __init__(self, dependencies: list[str]):
        self.dependencies = dependencies


class DynamicFieldFragment:
    def __init__(
        self,
        endpoint: str,
        requires: list[str],
        target: t.Literal["schema", "ui", "both"] = "schema",
        path: str = "",  # optional subpath, e.g. "enum" or "items.default"
    ):
        self.endpoint = endpoint
        self.requires = requires
        self.target = target
        self.path = path


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


# TODO else must only extend then, not if - rethink!
class Condition:
    def __init__(self, field: str, condition_only: bool = False):
        self.field = field
        self._condition_only = condition_only
        self._if: dict = {}
        self._then: dict | None = None
        self._else: dict | None = None

    def equals(self, value: t.Any) -> "Condition":
        self._if = {"properties": {self.field: {"const": value}}}
        return self

    def is_true(self) -> "Condition":
        return self.equals(True)

    def is_false(self) -> "Condition":
        return self.equals(False)

    def then_(self, **kwargs) -> "Condition":
        schema = Schema(**kwargs)
        self._then = schema.to_dict()
        return self

    def else_(self, **kwargs) -> "Condition":
        schema = Schema(**kwargs)
        self._else = schema.to_dict()
        return self

    def to_json(self) -> dict:
        if self._condition_only:
            return self._if["properties"]
        return {
            "if": self._if,
            "then": self._then,
            **({"else": self._else} if self._else is not None else {}),
        }


def if_(field: str) -> Condition:
    return Condition(field)


def requires(field: str) -> Condition:
    return Condition(field, condition_only=True)


IsConditional = type("_IsConditional", (), {})()


class CustomBaseModel(pdt.BaseModel):
    __with_ui__: dict[str, t.Any] | None = None
    __requires__: Condition | None = None
    __conditionals__: list[Condition] | None = None

    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        # TODO consider reordering the schema to be more readable
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

        if updated_props:
            schema["properties"] = updated_props
        else:
            del schema["properties"]

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
            if not ui_schema[field_name]:
                del ui_schema[field_name]

        return ui_schema

    @classmethod
    def model_requires(cls) -> dict | None:
        if cls.__requires__:
            return cls.__requires__.to_json()

    @classmethod
    def model_dependencies(cls) -> dict[str, list[str]]:
        deps: dict[str, list[str]] = {}

        for field_name, model_field in cls.model_fields.items():
            for meta in model_field.metadata:
                if isinstance(meta, DependsOn):
                    deps[field_name] = meta.dependencies

        return deps

    @classmethod
    def model_dynamic(cls) -> dict[str, list[dict]] | None:
        dynamic = {}
        for name, field in cls.model_fields.items():
            for meta in field.metadata:
                if isinstance(meta, DynamicFieldFragment):
                    dynamic.setdefault(name, []).append(
                        {
                            "endpoint": meta.endpoint,
                            "requires": meta.requires,
                            "target": meta.target,
                            "path": meta.path,
                        }
                    )
        return dynamic or None

    @classmethod
    def model_full_schema(cls) -> dict:
        schema = {}

        if requires := cls.model_requires():
            schema["requires"] = requires

        if dependencies := cls.model_dependencies():
            schema["dependencies"] = dependencies

        if dynamic := cls.model_dynamic():
            schema["dynamic"] = dynamic

        schema["schema"] = cls.model_json_schema()

        if ui_schema := cls.model_ui_schema():
            schema["ui"] = ui_schema

        return schema
