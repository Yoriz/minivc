'''
Created on 29 Sep 2012

@author: Dave Wilson
'''


from minivc import mvc

class CountVo(object):        
    def __init__(self):
        self.count = 0
        
    def increase(self):
        self.count += 1
        
    def decrease(self):
        self.count -= 1
     
class CountProxy(mvc.Proxy):

    CHANGED = "CountChanged"
    
    def __init__(self):
        super(CountProxy, self).__init__("CountProxy", CountVo())

    def increase(self):
        self.data.increase()
        self.send_note(CountProxy.CHANGED, self.data)
    
    def decrease(self):
        self.data.decrease()
        self.send_note(CountProxy.CHANGED, self.data)
        
class ViewDisplay(object):      
    def show_count(self, value):
        print "ViewDisplay count: %s" % value
        
class TestMediator(mvc.Mediator):
    def __init__(self, name, view):
        super(TestMediator, self).__init__(name, view)
        self.interests = [CountProxy.CHANGED]
        
    def handle_note(self, note):
        if note.name == CountProxy.CHANGED:
            self.view.show_count(note.body.count)

class TestFacade(mvc.Facade):
    
    STARTUP = "StartUp"
    
    def __init__(self):
        super(TestFacade, self).__init__()

    def start_up(self):
        view = ViewDisplay()
        self.send_note(TestFacade.STARTUP, view)


@mvc.register_command(TestFacade.STARTUP)
def startup_command(facade, note):
    print "startup_command", note
    prepare_models_command(facade)
    prepare_view_command(facade, note)
  
def prepare_models_command(facade):
    facade.register_proxy(CountProxy())
    
def prepare_view_command(facade, note):
    mediator = TestMediator("ViewDisplay", note.body)
    facade.register_mediator(mediator)
         
test_facade = TestFacade()
test_facade.start_up()
count_proxy = test_facade.get_proxy("CountProxy")
count_proxy.increase()
count_proxy.increase()
count_proxy.decrease()



