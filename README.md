## pydcr -- python dataclass (de)serialization

### features
- convert (nested) dataclasses to and from native python types  
- type conversion/checking on deserialization
  - otherwise no validation -- use dataclass `__post_init__`

### goals:
- easy to use
- expected behavior (particularly regarding inheritance and nested types)
- lightweight
