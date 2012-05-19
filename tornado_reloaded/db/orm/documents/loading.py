class Cache(object):
    """docstring for Cache"""
    def __init__(self):
        self.models   = {}
        self.waitings = {}
        
    def register(self, Model):
        """docstring for register"""
        name = Model.__name__
        self.models[name] = Model
        if name in self.waitings:
            for field in self.waitings[name]:
                field.rel = Model
            del self.waitings[name]
        
        return Model
        
    def get_model(self, name):
        """docstring for get_model"""
        return self.models.get(name)
        
    def wait_for_model(self, field, Model):
        """docstring for wait_for_model"""
        name = Model.metadata.name
        if name in self.models:
            return self.models[name]
        
        self.waitings.setdefault(name, []).append(field)
        
        return Model
        
cache = Cache()
        
def get_model(name):
    """docstring for get_model"""
    return cache.get_model(name)
    
def register(Model):
    """docstring for register"""
    return cache.register(Model)