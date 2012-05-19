from bisect import bisect

DEFAULT_NAMES = ('collection_name', 'name', 'plural_name', )

class Metadata(object):
    """docstring for Metadata"""
    def __init__(self, metadata):
        super(Metadata, self).__init__()
        self.fields = []
        self.model = None
        self.model_name = None
        self.name = None
        self.plural_name = None
        self.collection_name = None
        self.metadata = metadata
        
    def contribute_to_class(self, cls, name):
        """docstring for contribute_to_class"""
        cls.metadata = self
        self.name = cls.__name__
        self.plural_name = '%ss' % (self.name, )
        self.collection_name = '%ss' % (self.name.lower(), )
        self.model = cls
        
        if self.metadata:
            meta_attrs = self.metadata.__dict__.copy()
            for attr_name in DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                elif hasattr(self.metadata, attr_name):
                    setattr(self, attr_name, getattr(self.metadata, attr_name))
            
        
    def prepare(self, model):
        """docstring for prepare"""
        pass
        
    def add_field(self, field):
        """docstring for add_field"""
        bs = bisect(self.fields, field)
        self.fields.insert(bs, field)
        
    def get_field(self, name):
        for field in self.fields:
            if field.name == name:
                return field
                
        return None