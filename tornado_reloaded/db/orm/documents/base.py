from tornado_reloaded.db.orm.documents import loading
from tornado_reloaded.db.orm.documents.metadata import Metadata
from tornado_reloaded.db.orm.documents import fields
from tornado_reloaded.db.orm.documents.criteria import Criteria

from bson import ObjectId

class DocumentMetaclass(type):
    """docstring for DocumentMetaclass"""
    def __new__(cls, name, bases, attrs):
        Model = loading.get_model(name)
        if Model is not None:
            return Model
            
        super_new = super(DocumentMetaclass, cls).__new__
        parents = [base for base in bases if isinstance(base, DocumentMetaclass)]
        
        if not parents:
            return super_new(cls, name, bases, attrs)
            
        new_class = super_new(cls, name, bases, {'__module__': attrs.pop('__module__')})

        new_class.add_to_class('metadata', Metadata(attrs.pop('Metadata', None)))
            
        Criteria(new_class)
        
        for attr_name, attr in attrs.items():
            new_class.add_to_class(attr_name, attr)
        
        return loading.register(new_class)
        
    def add_to_class(cls, name, value):
        """docstring for add_to_class"""
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)
            
    def prepare(cls):
        """docstring for prepare"""
        metadata = cls.metadata
        metadata.prepare(cls)
        
        if cls.__doc__ is None:
            # cls.__doc__ = "%s(%s)" % (cls.__name__, ", ".join([f.attname for f in opts.fields]))           
            cls.__doc__ = "%s" % (cls.__name__, )
  
class Document(object):
    """docstring for Document"""
    __metaclass__ = DocumentMetaclass
    
    def __init__(self, *args, **kwargs):
        self._values = {}
        self._new_values = {}
        
        for name, value in kwargs.items():
            if name == '_id':
                name = 'pk'
            self._new_values[name] = value

    @classmethod
    def instance_for(cls, *args, **kwargs):
        """docstring for instance_for"""
        document = cls(*args, **kwargs)
        document._values = document._new_values
        document._new_values = {}
        return document
        
    def save(self):
        """docstring for save"""
        for _new_value_name, _new_value in self._new_values.items():
            print _new_value_name, ':', [self._values.get(_new_value_name), _new_value]
            
    def __getattr__(self, name):
        """docstring for __getattr__"""
        try:
            return self._new_values.get(name, self._values[name])
        except:
            raise AttributeError()
        
    def __getitem__(self, key):
        """docstring for __getitem__"""
        return self._new_values.get(key, self._values[key])
        
    def get(self, name, default=None):
        """docstring for get"""
        return self._new_values.get(name, self._values.get(name, default)) 