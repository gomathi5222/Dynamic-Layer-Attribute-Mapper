def classFactory(iface):
    from .dynamic_layer_attribute_mapper import DynamicLayerAttributeMapper
    return DynamicLayerAttributeMapper(iface)
