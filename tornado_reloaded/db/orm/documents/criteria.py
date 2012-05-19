import functools

from bson import ObjectId

from tornado_reloaded.db import get_db

class CriteriaContent(object):
    def __init__(self, model):
        """docstring for __init__"""
        self.model = None
        self._set = {}
        self._in = {}
        self.content = None
        
class CriteriaObject(object):
    """docstring for StringObject"""
    def __init__(self, criteria, initial_method_name):
        """docstring for __init__"""
        self.criteria = criteria
        self.initial_method_name = initial_method_name
        
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
            
    def __call__(self, *args, **kwargs):
        """docstring for __call__"""
        # print args, kwargs, getattr(self.criteria, self.initial_method_name)
        return getattr(self.criteria, self.initial_method_name)(*args, **kwargs)

class Criteria(object):
    """docstring for Critera"""
    def __init__(self, model, criteria_content=None):
        self.model = model
        self.callback = None
        self.spec = {}
        self.multiple = True
        self.only_first = False
        self.only_last = False
        if criteria_content is not None and callable(query):
            criteria_content = criteria_content(model)
        
        self.criteria_content = criteria_content or CriteriaContent(model)
        
        self.contribute_to_class(self.model)
        
    def contribute_to_class(self, cls):
        """docstring for contribute_to_class"""
        for method_name in ('all', 'count', 'exists', 'find', 'first', 'last', 'collection', 'where', 'response_to_object', ):
            setattr(cls, method_name, CriteriaObject(self, method_name))
            
    def __call__(self, callback, *args, **kwargs):
        """docstring for __call__"""
        self.callback = callback
        self.collection().find(spec=self.spec).loop(self.get_callback(self.multiple))
        
    def run_callback(self, response, multiple=True):
        """docstring for run_callback"""
        if self.callback:
            self.callback(self.response_to_object(response, multiple))
            
    def get_callback(self, multiple):
        """docstring for get_callback"""
        return functools.partial(self.run_callback, multiple=multiple)
        
    def all(self):
        """docstring for all"""
        self.multiple = True
        self.spec = {}
        return self
            
    def collection(self):
        """docstring for get_collection"""
        db = get_db()
        return getattr(db, self.model.metadata.collection_name)
        
    def count(self, callback):
        """docstring for all"""
        callback(0)
    
    def exists(self, callback):
        """docstring for all"""
        callback(True)
        
    def where(self, *args, **kwargs):
        """docstring for fname"""
        self.multiple = True
        
        for kwarg, value in kwargs.items():
            field = self.model.metadata.get_field(kwarg)
            if field is None:
                raise Exception()
            else:
                if field.localize:
                    self.spec['%s.en' % (field.name, )] = value
                else:
                    self.spec[field.name] = value
            
        return self
            
    def response_to_object(self, response, multiple=False):
        """docstring for response_to_object"""
        result = [self.model.instance_for(**item) for item in response]

        if self.only_first or not multiple:
            return result[0]
        elif self.only_last:
            return result[-1]
            
        return result

    def find(self, spec, *args, **kwargs):
        """docstring for all"""
        self.multiple = False
                
        if isinstance(spec, (unicode, str, basestring, )):
            self.spec['_id'] = ObjectId(spec)
        elif isinstance(spec, (list, tuple, )):
            self.multiple = True
            self.spec['_id'] = {
                '$in' : [ObjectId(elt) for elt in spec]
            }
        elif not isinstance(spec, ObjectId):
            raise Exception()
                
        return self
        
    def one(self):
        """docstring for one"""
        self.multiple = False
        
        return self
        
    def first(self):
        """docstring for first"""
        self.only_first = True
        
        return self
        
    def last(self):
        """docstring for last"""
        self.only_last = True
        
        return self
        