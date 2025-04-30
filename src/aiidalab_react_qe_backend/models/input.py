SCHEMA = {
    "basic": {
        "schema": {
            "type": "object",
            "definitions": {
                "relax": {"type": "string", "title": "Relaxation level"},
                "electronic_type": {
                    "type": "string",
                    "title": "Electronic type",
                    "enum": ["metallic", "insulator"],
                    "default": "metallic",
                },
                "protocol": {
                    "type": "string",
                    "title": "Protocol",
                    "enum": ["fast", "balanced", "stringent"],
                    "default": "fast",
                },
                "magnetism": {"type": "boolean", "title": "Magnetism"},
                "spin_orbit": {"type": "boolean", "title": "Spin orbit coupling"},
            },
            "properties": {
                "relax": {"$ref": "#/definitions/relax"},
                "electronic_type": {"$ref": "#/definitions/electronic_type"},
                "protocol": {"$ref": "#/definitions/protocol"},
                "magnetism": {"$ref": "#/definitions/magnetism"},
                "spin_orbit": {"$ref": "#/definitions/spin_orbit"},
            },
            "if": {"properties": {"molecule": {"const": True}}},
            "then": {
                "properties": {
                    "relax": {"enum": ["none", "positions"], "default": "positions"}
                }
            },
            "else": {
                "properties": {
                    "relax": {
                        "enum": ["none", "positions", "positions-cell"],
                        "default": "positions-cell",
                    }
                }
            },
        },
        "ui": {
            "relax": {
                "ui:widget": "toggleGroup",
                "ui:enumNames": [
                    "Structure as is",
                    "Positions only",
                    "Full geometry",
                ],
            },
            "electronic_type": {
                "ui:widget": "toggleGroup",
                "ui:enumNames": ["Metallic", "Insulator"],
            },
            "protocol": {
                "ui:widget": "toggleGroup",
                "ui:enumNames": ["Fast", "Balanced", "Stringent"],
            },
        },
        "dependencies": ["structure.pbc"],
    },
    "advanced": {
        "convergence": {
            "schema": {
                "type": "object",
                "title": "Convergence",
                "definitions": {
                    "scfConvEng": {
                        "type": "number",
                        "title": "SCF energy (Ry/atom)",
                    },
                    "ionicConvEng": {
                        "type": "number",
                        "title": "Ionic energy (Ry/atom)",
                    },
                    "ionicConvForce": {
                        "type": "number",
                        "title": "Ionic force (Ry/Bohr)",
                    },
                },
                "properties": {
                    "scfConvEng": {"$ref": "#/definitions/scfConvEng"},
                    "ionicConvEng": {"$ref": "#/definitions/ionicConvEng"},
                    "ionicConvForce": {"$ref": "#/definitions/ionicConvForce"},
                },
                "if": {"properties": {"protocol": {"const": "fast"}}},
                "then": {
                    "properties": {
                        "scfConvEng": {"default": 4e-10},
                        "ionicConvEng": {"default": 0.0001},
                        "ionicConvForce": {"default": 0.001},
                    }
                },
                "else": {
                    "if": {"properties": {"protocol": {"const": "balanced"}}},
                    "then": {
                        "properties": {
                            "scfConvEng": {"default": 2e-10},
                            "ionicConvEng": {"default": 0.00001},
                            "ionicConvForce": {"default": 0.0001},
                        }
                    },
                    "else": {
                        "properties": {
                            "scfConvEng": {"default": 1e-10},
                            "ionicConvEng": {"default": 0.000005},
                            "ionicConvForce": {"default": 0.00005},
                        }
                    },
                },
            },
            "ui": {"protocol": {"ui:widget": "hidden"}},
            "dependencies": ["basic.protocol"],
        },
        "smearing": {
            "schema": {
                "type": "object",
                "title": "Smearing",
                "definitions": {
                    "method": {
                        "type": "string",
                        "title": "Smearing",
                        "enum": ["Gaussian", "Methfessel-Paxton", "Fermi-Dirac"],
                        "default": "Gaussian",
                    },
                    "width": {
                        "type": "number",
                        "title": "Width (eV)",
                        "default": 0.05,
                    },
                },
                "properties": {
                    "method": {"$ref": "#/definitions/method"},
                    "width": {"$ref": "#/definitions/width"},
                },
            }
        },
        "magnetization": {
            "includedIf": {"basic.magnetism": {"const": True}},
            "schema": {
                "type": "object",
                "title": "Magnetization",
                "definitions": {
                    "mode": {
                        "type": "string",
                        "title": "Input mode",
                        "enum": ["moments", "total"],
                        "default": "moments",
                    },
                    "tot_magnetization": {
                        "type": "number",
                        "title": "Total magnetization",
                        "minimum": 0,
                        "multipleOf": 0.1,
                        "default": 1,
                    },
                    "moments": {
                        "type": "array",
                        "title": "Initial magnetic moments",
                        "items": {"type": "number", "default": 0.1},
                    },
                },
                "if": {"properties": {"electronic_type": {"const": "insulator"}}},
                "then": {
                    "properties": {
                        "tot_magnetization": {"$ref": "#/definitions/tot_magnetization"}
                    }
                },
                "else": {
                    "properties": {"mode": {"$ref": "#/definitions/mode"}},
                    "if": {"properties": {"mode": {"const": "moments"}}},
                    "then": {
                        "properties": {"moments": {"$ref": "#/definitions/moments"}}
                    },
                    "else": {
                        "properties": {
                            "tot_magnetization": {
                                "$ref": "#/definitions/tot_magnetization"
                            }
                        }
                    },
                },
            },
            "ui": {
                "mode": {
                    "ui:widget": "toggleGroup",
                    "ui:enumNames": [
                        "Initial magnetic moments",
                        "Total magnetization",
                    ],
                },
                "moments": {
                    "ui:options": {"classNames": "mt-2"},
                    "items": {
                        "generatedFrom": "structure.species",
                        "template": "{{species}}",
                    },
                },
            },
            "dependencies": ["basic.electronic_type"],
        },
        "hubbardU": {
            "schema": {
                "type": "object",
                "title": "Hubbard U",
                "definitions": {
                    "use_hubbard": {
                        "type": "boolean",
                        "title": "Enable U",
                        "default": False,
                    },
                    "U": {
                        "type": "number",
                        "title": "U (eV)",
                        "minimum": 0,
                        "default": 0,
                    },
                },
                "properties": {"use_hubbard": {"$ref": "#/definitions/use_hubbard"}},
                "if": {"properties": {"use_hubbard": {"const": True}}},
                "then": {"properties": {"U": {"$ref": "#/definitions/U"}}},
            }
        },
        "pseudopotentials": {
            "schema": {
                "type": "object",
                "title": "Pseudopotentials",
                "definitions": {
                    "functional": {
                        "type": "string",
                        "title": "Functional",
                        "enum": ["PBE", "PBEsol"],
                        "default": "PBEsol",
                    },
                    "family": {"type": "string", "title": "Family"},
                    "accuracy": {"type": "string", "title": "Accuracy"},
                    "pseudopotentials": {
                        "type": "array",
                        "title": "Pseudopotentials",
                        "items": {"type": "string", "format": "data-url"},
                    },
                },
                "properties": {
                    "functional": {"$ref": "#/definitions/functional"},
                    "family": {"$ref": "#/definitions/family"},
                    "accuracy": {"$ref": "#/definitions/accuracy"},
                    "pseudopotentials": {"$ref": "#/definitions/pseudopotentials"},
                },
                "if": {"properties": {"spin_orbit": {"const": False}}},
                "then": {
                    "properties": {
                        "family": {
                            "enum": ["SSSP", "PseudoDojo"],
                            "default": "SSSP",
                        }
                    },
                    "if": {"properties": {"family": {"const": "SSSP"}}},
                    "then": {
                        "properties": {
                            "accuracy": {
                                "enum": ["Efficiency", "Precision"],
                                "default": "Efficiency",
                            }
                        }
                    },
                    "else": {
                        "properties": {
                            "accuracy": {
                                "enum": ["Standard", "Stringent"],
                                "default": "Standard",
                            }
                        }
                    },
                },
                "else": {
                    "properties": {
                        "family": {"enum": ["PseudoDojo"], "default": "PseudoDojo"},
                        "accuracy": {
                            "enum": ["Standard", "Stringent"],
                            "default": "Standard",
                        },
                    }
                },
            },
            "ui": {
                "functional": {"ui:widget": "toggleGroup"},
                "family": {"ui:widget": "toggleGroup"},
                "accuracy": {"ui:widget": "toggleGroup"},
                "pseudopotentials": {
                    "ui:options": {"classNames": "mt-2"},
                    "items": {
                        "ui:hideError": True,
                        "ui:options": {"accept": ".UPF"},
                        "generatedFrom": "structure.species",
                        "template": "{{species}}",
                    },
                },
            },
            "dependencies": ["basic.spin_orbit"],
        },
    },
}
