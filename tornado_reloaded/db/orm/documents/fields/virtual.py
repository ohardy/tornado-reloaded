class VirtualObject(object):
    """docstring for VirtualObject"""
    def __init__(self, field):
        """docstring for __init__"""
        self.field = field
    
    def contribute_to_class(self, cls, name):
        """docstring for contribute_to_class"""
        setattr(cls, name, self)
        

class StringObject(VirtualObject):
    """docstring for StringObject"""
    def __get__(self, instance, instance_type=None):
        """docstring for __get__"""
        if instance is None:
            return self
            
        value = instance._new_values.get(self.field.attname, instance._values.get(self.field.attname))
        
        return value
        
    def __set__(self, instance, value):
        """docstring for __set__"""
        if instance is None:
            raise Exception()
        
        if value is not None:
            instance._new_values[self.field.attname] = value