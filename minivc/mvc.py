"""
MiniVC - a simple, small, MVC library for python. no frameworks of any kind included.
mvc. if nothing else, we can throw the laundry that is our code into three different piles.
inspired by puremvc python by Toby de Havilland <toby.de.havilland@puremvc.org>
"""

# todo move me into a distributable package and put on pypi. and seperate git repo

from functools import partial

class Duplicate(Exception): pass

class NotFound(Exception): pass

class InvalidMap(Exception): pass

class FactoryOnly(Exception): pass

class Singleton(object):
    """singleton check. only instantiates when passed a string key"""

    def __init__(self, *args):
        if args[-1] is not 'there_can_be_only_one':
            raise FactoryOnly('singletons cant be instantiated directly')


class Controller(Singleton):
    """singleton. manages controller objects"""

    def __init__(self, *args):
        Singleton.__init__(self, *args)
        self.view = get_view()
        self.command_map = { }

    def handle_note(self, note):
        try:
            cmd = self.command_map[note['name']]#().handle_note(note)
            if isinstance(cmd, type) or hasattr(cmd, '__is_instance__'): # has attr check is for pyjs. isintance(cmd, type) fails in pyjs?.
                cmd().handle_note(note) # class based controller
            else:
                cmd(get_facade()) # function based controller
        except KeyError:
            raise NotFound('no such command: %s' % note['name'])

    def register_command(self, name, cmd): # cmd is a controller function or a controller class
        if name in self.command_map:
            raise Duplicate('there is already a command with name %s: %s' % (name, self.command_map[name]))
        self.view.register_observer(name, { 'func': self.handle_note, 'obj': self })
        self.command_map[name] = cmd

    def remove_command(self, name):
        if name in self.command_map:
            self.view.remove_observer(name, self)
            del self.command_map[name]

class Model(Singleton):
    """singleton. manages model objects"""

    def __init__(self, *args):
        Singleton.__init__(self, *args)
        self.proxy_map = { }

    def register_proxy(self, proxy):
        self.proxy_map[proxy.name] = proxy
        proxy.on_register()
        return proxy

    def get_proxy(self, name):
        return self.proxy_map.get(name, None)

    def remove_proxy(self, name):
        proxy = self.proxy_map.get(name, None)
        if proxy:
            del self.proxy_map[name]
            proxy.on_remove()

class View(Singleton):
    """singleton. manages view objects"""

    def __init__(self, *args):
        Singleton.__init__(self, *args)
        self.observer_map = { }
        self.mediator_map = { }

    def register_observer(self, name, observer):
        if { 'func', 'obj' } != set(observer.keys()):
            raise InvalidMap("observer should be {'func':f, 'obj':o}")
        if not name in self.observer_map:
            self.observer_map[name] = []
        observers = self.observer_map[name]
        if observer['obj'] in [o['obj'] for o in observers]:
            raise Duplicate('obj: %s is already observing note.name: %s' % (observer['obj'], name))
        observers.append(observer)

    def notify_observers(self, note):
        for observer in self.observer_map.get(note['name'], []):
            observer['func'](note)

    def remove_observer(self, name, obj):
        observers = self.observer_map[name]
        for observer in observers:
            if observer['obj'] is obj:
                observers.remove(observer)
                break

    def register_mediator(self, mediator):
        if mediator.name in self.mediator_map:
            raise Duplicate('mediator with name "%s" already registered.' % mediator.name)
        self.mediator_map[mediator.name] = mediator
        for interest in mediator.interests:
            self.register_observer(interest, { 'func': mediator.handle_note, 'obj': mediator })
        mediator.on_register()
        return mediator

    def get_mediator(self, name):
        return self.mediator_map.get(name, None)

    def remove_mediator(self, name):
        mediator = self.get_mediator(name)
        if not mediator:
            raise NotFound('no mediator with name "%s" to remove.' % name)
        for interest in mediator.interests:
            self.remove_observer(interest, mediator)
        del self.mediator_map[name]
        mediator.on_remove()

class Facade(Singleton):
    """singleton. instantiates the mvc and exposes their api's"""

    def __init__(self, commands=[], *args): # commands = [ ('name', Command), ]
        if not isinstance(commands, list): # when called without commands list, fix the signature
            args = tuple([commands])
            commands = []
        Singleton.__init__(self, *args)
        self.controller = get_controller()
        self.model = get_model()
        self.view = get_view()
        self.build_api()
        if isinstance(commands, list): # when instantiated without commands list, this is needed
            for name, Command in commands:
                self.register_command(name, Command)

    def build_api(self):
        self.register_command = self.controller.register_command
        self.register_proxy = self.model.register_proxy
        self.register_mediator = self.view.register_mediator
        self.remove_command = self.controller.remove_command
        self.remove_proxy = self.model.remove_proxy
        self.remove_mediator = self.view.remove_mediator
        self.get_proxy = self.model.get_proxy
        self.get_mediator = self.view.get_mediator

    def send_note(self, name, body=None):
        self.view.notify_observers({ 'name': name, 'body': body })

class Generic(object):
    """inherit me for generic mvc object"""

    def __init__(self, name):
        self.name = name
        self.facade = Facade()
        self.send_note = self.facade.send_note

    def on_register(self): pass

    def on_remove(self): pass

def command(facade):
    """use this signature for a function based controller"""
    pass


class Command(object):
    """extend me for a class based controller"""

    def __init__(self):
        self.facade = get_facade()
        self.send_note = self.facade.send_note

    def handle_note(self, note): pass

class Proxy(Generic):
    """extend me for a model object"""
    name = ''

    def __init__(self, name):
        self.name = name
        self.facade = get_facade()

class Mediator(Generic):
    """extend me for a view object """
    name = ''

    interests = [] # must be defined in subclass, not dynamically inserted

    def handle_note(self, note): pass # called whenever a note is sent who's name is listed in self.interests

singletons = { }

def singleton_factory(name, cls, *args, **kwargs):
    if not name in singletons:
        args += tuple(['there_can_be_only_one'])
        singletons[name] = cls(*args, **kwargs)
    return singletons[name]

get_controller = partial(singleton_factory, 'controller', Controller)
get_model = partial(singleton_factory, 'model', Model)
get_view = partial(singleton_factory, 'view', View)
get_facade = partial(singleton_factory, 'facade', Facade)
get_facade.__doc__ = 'pass in a list of command pairs. ie, [ ("startup", StartupCommand), ]'


