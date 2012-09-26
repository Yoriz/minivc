import minivc.mvc
from minivc.mvc import Command, Duplicate, NotFound, get_view, get_facade, get_controller, get_model
from nts.lib.unittest import TestCase

class TestMvc(TestCase):
    def setup(self):
        minivc.mvc.singletons = { } # reset the singletons records

    def test_singleton(self):
        get_view() is get_view()
        get_model() is get_model()
        get_controller() is get_controller()
        get_facade() is get_facade()

    def test_controller(self):
        c = get_controller()

        class Cmd(object):
            output = ''
            body = None

            def handle_note(self, note):
                if not self.output and not self.body:
                    Cmd.output = 'handled'
                    Cmd.body = note['body']
                else:
                    Cmd.output = ''
                    Cmd.body = None

        name_ctrl_class = 'cmd'
        c.register_command(name_ctrl_class, Cmd)
        self.assert_raises(Duplicate, lambda: c.register_command(name_ctrl_class, Cmd))
        note = { 'name': name_ctrl_class, 'body': 123 }
        c.handle_note(note)
        assert Cmd.output is 'handled'
        assert Cmd.body is 123
        c.handle_note(note)
        assert Cmd.output is ''
        assert Cmd.body is None
        c.remove_command(name_ctrl_class)
        self.assert_raises(NotFound, lambda: c.handle_note(note))
        assert Cmd.output is ''
        assert Cmd.body is None

        facade = get_facade()
        facade.output = ''

        def cmd(facade):
            if facade.output is '':
                facade.output = 'handled'
            else:
                facade.output = ''

        name_ctrl_func = 'cmdfunc'
        note = { 'name': name_ctrl_func, 'body': 123 }
        c.register_command(name_ctrl_func, cmd)
        assert facade.output is ''
        c.handle_note(note)
        assert facade.output is 'handled'
        c.remove_command(name_ctrl_func)
        self.assert_raises(NotFound, lambda: c.remove_command(name_ctrl_func))
        assert facade.output is 'handled'


    def test_model(self):
        m = get_model()
        proxy_name = 'some_proxy'

        class Proxy(object):
            name = proxy_name

            def on_register(self): pass

            def on_remove(self): pass


        proxy = Proxy()
        m.register_proxy(proxy)
        assert proxy is m.get_proxy(proxy_name)
        m.remove_proxy(proxy_name)
        assert m.get_proxy(proxy_name) is None

    def test_view(self):
        v = get_view()
        self.output = ''

        def func(*args):
            if not self.output:
                self.output = 'called'
            else:
                self.output = ''

        note_name = 'some_note'
        note = { 'name': note_name, 'body': None }
        observer = { 'func': func, 'obj': self }
        v.register_observer(note_name, observer)
        self.assert_raises(Duplicate, lambda: v.register_observer(note_name, observer))
        v.notify_observers(note)
        assert 'called' is self.output
        v.remove_observer(note_name, self)
        v.notify_observers(note)
        assert 'called' is self.output
        delattr(self, 'output')

        mediator_name = 'some_mediator'

        class Mediator(object):
            interests = [note_name]
            name = mediator_name
            output = ''

            def on_register(self): pass

            def on_remove(self): pass

            def handle_note(self, note):
                if not Mediator.output:
                    Mediator.output = note['name']
                else:
                    Mediator.output = ''

        mediator = Mediator()
        v.register_mediator(mediator)
        self.assert_raises(Duplicate, lambda: v.register_mediator(mediator))
        assert mediator is v.get_mediator(mediator_name)
        assert '' is Mediator.output
        v.notify_observers(note)
        assert note_name is Mediator.output
        v.remove_mediator(mediator_name)
        self.assert_raises(NotFound, lambda: v.remove_mediator(mediator_name))
        assert v.get_mediator(mediator_name) is None
        v.notify_observers(note)
        assert note_name is Mediator.output

    def test_facade(self):
        mediator_name = 'some_mediator'
        note_name = 'cmd1'

        class Mediator(object):
            interests = [note_name]
            name = mediator_name
            output = ''

            def on_register(self): pass

            def on_remove(self): pass

            def handle_note(self, note):
                if not Mediator.output:
                    Mediator.output = note['name']
                else:
                    Mediator.output = ''

        class Command1(Command):
            output = ''

            def handle_note(self, note):
                if not self.output:
                    Command1.output = 'handled'
                else:
                    Command1.output = ''

        f = get_facade([(note_name, Command1), ])
        f.register_mediator(Mediator())
        assert '' is Command1.output is Mediator.output
        f.send_note(note_name)
        assert 'handled' is Command1.output and note_name is Mediator.output
        f.send_note(note_name)
        assert '' is Command1.output is Mediator.output
        f.remove_mediator(mediator_name)
        f.send_note(note_name)
        assert 'handled' is Command1.output and '' is Mediator.output

if __name__ == '__main__':
    TestMvc()._run_all()








