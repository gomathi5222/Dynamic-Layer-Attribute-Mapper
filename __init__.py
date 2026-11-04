def classFactory(iface):
    from .dynamic_layer_attribute_mapper import WardBoundaryMapper
    return WardBoundaryMapper(iface)