from virtual import StringObject

class Field(object):
    """docstring for Field"""
    creation_counter = 0
    
    def __init__(self, label=None, localize=False):
        self.label = label
        self.localize = localize
        
    def contribute_to_class(self, cls, name):
        """docstring for contribute_to_class"""
        self.name = name
        self.document = cls
        cls.metadata.add_field(self)
        setattr(cls, self.name, StringObject(self))
        
    def get_attname(self):
        return self.name
        
    @property
    def attname(self):
        return self.get_attname()
    
        
class ArrayField(Field):
    """docstring for ArrayField"""
    pass
    
class BooleanField(Field):
    """docstring for ArrayField"""
    pass

class DateField(Field):
    """docstring for ArrayField"""
    pass

class DateTimeField(Field):
    """docstring for ArrayField"""
    pass

class FloatField(Field):
    """docstring for ArrayField"""
    pass

class DictField(Field):
    """docstring for ArrayField"""
    pass

class RangeField(Field):
    """docstring for ArrayField"""
    pass

class StringField(Field):
    """docstring for ArrayField"""
    pass

class SymbolField(Field):
    """docstring for ArrayField"""
    pass

class TimeField(Field):
    """docstring for ArrayField"""
    pass
