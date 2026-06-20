"""
Tiny module holding the object definition registry.

Separated so that individual object definition modules can register themselves
without creating a circular import with engine.world_builder (which is still
initializing when the definitions are loaded).

repo : https://github.com/openmarmot/twe
"""

OBJECT_REGISTRY = {}


def register_object(object_type):
    """Decorator to register a builder function by its world_builder_identity string."""
    def decorator(builder_fn):
        OBJECT_REGISTRY[object_type] = builder_fn
        return builder_fn
    return decorator
