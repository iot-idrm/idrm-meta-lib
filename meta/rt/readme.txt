resource type name:
==================
sample:
lwm2m.1
oic.r.switch.binary
iconnect.humidity

folder structure
====================
the first level folder is the first section of resource type name


meta file name
=========================
the file name should identical with the resource tyep name


meta file sample
=========================
A resource type meta file is a JSON file,  which is a jsonArray
includes many json objects. Each level-1 json object represents
a resource type. The whole meta file is close to the OCF
definition.

[
    {
        "title": "It is a title",
        "definitions": {
            "rt": "oic.r.airflow",
            "description": "description of the resource",
            "properties": [
            {
                "name": "speed",
                "type": "String",
                "description": "description of the property",
                "readOnly": true,
                "ext": [
                {
                    "ext_n": "default_unit",
                    "ext_v": "cm"
                }
                ]
            },
            {
                "name": "direction",
                "type": "String",
                "description": "description of the property"
            },
            {
                "name": "supportdirections",
                "type": "array",
                "items":
                {
                    "type":
                        "string",
                    "minItems":
                        1,
                    "uniqueItems":
                        true
                }
            }
            ],
            "required": [
                "supportdirections",
                "direction"
            ],
            "type": "object"
        }
    }
]
