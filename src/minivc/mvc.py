"""
MiniVC - a small and simple, mvc library for python. it doesn't do much. thats a feature.
mvc, so if nothing else, we can throw the laundry that is our code into three different piles.
inspired by puremvc python by Toby de Havilland <toby.de.havilland@puremvc.org>
"""

# Forked from nathants

from collections import namedtuple

Note = namedtuple("Note", "name, body, uid")

class Controller(object):
    """singleton. manages controller objects"""
    _shared_state = {}
    _command_map = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        self.view = View()

    def handle_note(self, note):
        cmd = self._command_map[note.name]
        cmd(Facade(), note)

    def register_command(self, name, cmd):
        observer = {"func": self.handle_note, "obj": self}
        self.view.register_observer(name, observer)
        self._command_map[name] = cmd

    def remove_command(self, name):
        if name in self._command_map:
            self.view.remove_observer(name, self)
            del self._command_map[name]

class Model(object):
    """singleton. manages model objects"""
    _shared_state = {}
    _proxy_map = {}

    def __init__(self):
        self.__dict__ = self._shared_state

    def register_proxy(self, proxy):
        self._proxy_map[proxy.name] = proxy
        proxy.on_register()
        return proxy

    def get_proxy(self, name):
        proxy = self._proxy_map.get(name, None)
        if not proxy:
            raise LookupError("No Proxy found for name: %s" % name)
        return proxy

    def remove_proxy(self, name):
        proxy = self._proxy_map.get(name, None)
        if proxy:
            del self._proxy_map[name]
            proxy.on_remove()

class View(object):
    """singleton. manages view objects"""
    _shared_state = {}
    _observer_map = {}
    _mediator_map = {}

    def __init__(self):
        self.__dict__ = self._shared_state

    def register_observer(self, name, observer):
        if not name in self._observer_map:
            self._observer_map[name] = []
        observers = self._observer_map[name]
        observers.append(observer)

    def notify_observers(self, note):
        for observer in self._observer_map.get(note.name, []):
            observer["func"](note)

    def remove_observer(self, name, obj):
        observers = self._observer_map[name]
        for observer in observers:
            if observer["obj"] is obj:
                observers.remove(observer)
                break

    def register_mediator(self, mediator):
        self._mediator_map[mediator.name] = mediator
        for interest in mediator.interests:
            observer = {"func": mediator.handle_note, "obj": mediator}
            self.register_observer(interest, observer)
        mediator.on_register()
        return mediator

    def get_mediator(self, name):
        mediator = self._mediator_map.get(name, None)
        if not mediator:
            raise LookupError("No Mediator found for name: %s" % name)
        return mediator

    def remove_mediator(self, name):
        mediator = self.get_mediator(name)
        for interest in mediator.interests:
            self.remove_observer(interest, mediator)
        del self._mediator_map[name]
        mediator.on_remove()

class Facade(object):
    """singleton. instantiates the mvc and exposes their api's"""
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        self.controller = Controller()
        self.model = Model()
        self.view = View()
        self.register_command = self.controller.register_command
        self.register_proxy = self.model.register_proxy
        self.register_mediator = self.view.register_mediator
        self.remove_command = self.controller.remove_command
        self.remove_proxy = self.model.remove_proxy
        self.remove_mediator = self.view.remove_mediator
        self.get_proxy = self.model.get_proxy
        self.get_mediator = self.view.get_mediator

    def send_note(self, name, body=None, uid=None):
        self.view.notify_observers(Note(name, body, uid))

def command(facade, note): 
    """use this signature for a controller"""
    print facade, note

def register_command(name):
    """decorator to register a command with the controller"""

    def register(cmd):
        Facade().register_command(name, cmd)
        return cmd

    return register

class Proxy(object):
    """extend me for a model object"""
    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        self.facade = Facade()
        self.send_note = self.facade.send_note

    def on_register(self): pass

    def on_remove(self): pass

class Mediator(object):
    """extend me for a view object """
    interests = [] # must be defined in subclass, not dynamically inserted
    
    def __init__(self, name, view=None):
        self.name = name
        self.view = view
        self.facade = Facade()
        self.send_note = self.facade.send_note

    def on_register(self): pass

    def on_remove(self): pass
    
    def handle_note(self, note): pass # called whenever a note is sent who's name is listed in self.interests
