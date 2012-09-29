"""
MiniVC - a small and simple, mvc library for python. it doesn't do much. thats a feature.
mvc, so if nothing else, we can throw the laundry that is our code into three different piles.
inspired by puremvc python by Toby de Havilland <toby.de.havilland@puremvc.org>
"""

# todo move me into a distributable package and put on pypi. and seperate git repo


class Controller(object):
    """singleton. manages controller objects"""
    _shared_state = {}
    _command_map = {}

    def __init__(self):
        self.__dict__ = self._shared_state
        self.view = View()

    def handle_note(self, note):
        assert note['name'] in self._command_map,\
                                    'no such command: {0}'.format(note['name'])
        cmd = self._command_map[note['name']]
        cmd(Facade(), note)

    def register_command(self, name, cmd): # cmd is a controller function or a controller class
        assert name not in self._command_map,\
                                'there is already a command with name {0}: {1}'\
                                .format(name,self._command_map[name])
        self.view.register_observer(name, { 'func': self.handle_note,
                                           'obj': self })
        self._command_map[name] = cmd

    def remove_command(self, name):
        if name in self._command_map:
            self.view.remove_observer(name, self)
            del self._command_map[name]

class Model(object):
    """singleton. manages model objects"""
    _shared_state = {}
    _proxy_map = { }

    def __init__(self):
        self.__dict__ = self._shared_state

    def register_proxy(self, proxy):
        assert proxy.name not in self._proxy_map,\
                    'proxy with name {0} already registered'.format(proxy.name)
        self._proxy_map[proxy.name] = proxy
        proxy.on_register()
        return proxy

    def get_proxy(self, name):
        return self._proxy_map.get(name, None)

    def remove_proxy(self, name):
        proxy = self._proxy_map.get(name, None)
        if proxy:
            del self._proxy_map[name]
            proxy.on_remove()

class View(object):
    """singleton. manages view objects"""
    _shared_state = {}
    _observer_map = { }
    _mediator_map = { }

    def __init__(self):
        self.__dict__ = self._shared_state

    def register_observer(self, name, observer):
        assert { 'func', 'obj' } == set(observer.keys()),\
                                        "observer should be {'func':f, 'obj':o}"
        if not name in self._observer_map:
            self._observer_map[name] = []
        observers = self._observer_map[name]
        assert observer['obj'] not in [o['obj'] for o in observers],\
                                'obj: {0} is already observing note.name: {1}'.\
                                format(observer['obj'], name)
        observers.append(observer)

    def notify_observers(self, note):
        for observer in self._observer_map.get(note['name'], []):
            observer['func'](note)

    def remove_observer(self, name, obj):
        observers = self._observer_map[name]
        for observer in observers:
            if observer['obj'] is obj:
                observers.remove(observer)
                break

    def register_mediator(self, mediator):
        assert mediator.name not in self._mediator_map,\
            'mediator with name "{0}" already registered.'.format(mediator.name)
        self._mediator_map[mediator.name] = mediator
        for interest in mediator.interests:
            self.register_observer(interest, { 'func': mediator.handle_note,
                                              'obj': mediator })
        mediator.on_register()
        return mediator

    def get_mediator(self, name):
        return self._mediator_map.get(name, None)

    def remove_mediator(self, name):
        mediator = self.get_mediator(name)
        assert mediator, 'no mediator with name "{0}" to remove.'.format(name)
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

    def send_note(self, name, body=None):
        self.view.notify_observers({ 'name': name, 'body': body })

def command(facade, note):
    """use this signature for a controller"""
    pass

def register_command(name):
    """decorator to register a command with the controller"""

    def register(cmd):
        Facade().register_command(name, cmd)
        return cmd

    return register

class Proxy(object):
    """extend me for a model object"""

    name = ''

    def __init__(self, name):
        self.name = name
        self.facade = Facade()
        self.send_note = self.facade.send_note

    def on_register(self): pass

    def on_remove(self): pass

class Mediator(Proxy):
    """extend me for a view object """

    interests = [] # must be defined in subclass, not dynamically inserted

    def handle_note(self, note): pass # called whenever a note is sent who's name is listed in self.interests
