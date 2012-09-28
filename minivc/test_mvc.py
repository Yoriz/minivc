import minivc.mvc
from minivc.mvc import get_view, get_facade, get_controller, get_model, register_command, Mediator, Proxy
from nathants.lib.unittest import TestCase

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
        f = get_facade()

        f.output = ''
        f.body = None
        name = 'cmd'

        @register_command(name)
        def command(f, note):
            if not f.output:
                f.output = 'handled'
                f.body = note['body']
            else:
                f.output = ''
                f.body = None

        self.assert_raises(AssertionError, lambda: c.register_command(name, command))
        note = { 'name': name, 'body': 123 }
        c.handle_note(note)
        assert f.output is 'handled'
        assert f.body is 123
        c.handle_note(note)
        assert f.output is ''
        assert f.body is None
        c.remove_command(name)
        self.assert_raises(AssertionError, lambda: c.handle_note(note))
        assert f.output is ''
        assert f.body is None

        facade = get_facade()
        facade.output = ''

        def cmd(facade, note):
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
        self.assert_raises(AssertionError, lambda: c.remove_command(name_ctrl_func))
        assert facade.output is 'handled'


    def test_model(self):
        m = get_model()
        proxy_name = 'some_proxy'

        class Prx(Proxy):
            name = proxy_name

            def on_register(self): pass

            def on_remove(self): pass

        proxy = Prx()
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
        self.assert_raises(AssertionError, lambda: v.register_observer(note_name, observer))
        v.notify_observers(note)
        assert 'called' is self.output
        v.remove_observer(note_name, self)
        v.notify_observers(note)
        assert 'called' is self.output
        delattr(self, 'output')

        mediator_name = 'some_mediator'

        class Med(Mediator):
            interests = [note_name]
            name = mediator_name
            output = ''

            def on_register(self): pass

            def on_remove(self): pass

            def handle_note(self, note):
                if not Med.output:
                    Med.output = note['name']
                else:
                    Med.output = ''

        mediator = Med()
        v.register_mediator(mediator)
        self.assert_raises(AssertionError, lambda: v.register_mediator(mediator))
        assert mediator is v.get_mediator(mediator_name)
        assert '' is Med.output
        v.notify_observers(note)
        assert note_name is Med.output
        v.remove_mediator(mediator_name)
        self.assert_raises(AssertionError, lambda: v.remove_mediator(mediator_name))
        assert v.get_mediator(mediator_name) is None
        v.notify_observers(note)
        assert note_name is Med.output

    def test_facade(self):
        f = get_facade()
        mediator_name = 'some_mediator'
        note_name = 'cmd1'

        class Med(Mediator):
            interests = [note_name]
            name = mediator_name
            output = ''

            def on_register(self): pass

            def on_remove(self): pass

            def handle_note(self, note):
                if not Med.output:
                    Med.output = note['name']
                else:
                    Med.output = ''

        f.output = ''
        
        @register_command(note_name)
        def command(f, note):
            if not f.output:
                f.output = 'handled'
            else:
                f.output = ''

        f.register_mediator(Med())
        assert '' is f.output is Med.output
        f.send_note(note_name)
        assert 'handled' is f.output# and note_name is Med.output
        f.send_note(note_name)
        assert '' is f.output is Med.output
        f.remove_mediator(mediator_name)
        f.send_note(note_name)
        assert 'handled' is f.output and '' is Med.output

if __name__ == '__main__':
    TestMvc()._run_all()








