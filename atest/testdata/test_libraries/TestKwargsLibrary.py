class TestKwargsLibrary:

    def __init__(self):
        self.command = ""
        self.args = ()
        self.kwargs = {}

    def vargs_and_kwargs(self, command, *args, **kwargs):
        self.command = command
        self.args = args
        self.kwargs = kwargs
        print self
        assert(command == "my command")
        assert(args == ("sdfsdfsf",))
        assert(kwargs == {"jada":"bada", "kwow":"we2222"})

    def only_kwargs(self, def1="my default value", **kwargs):
        self.command = None
        self.args = None
        self.kwargs = kwargs
        print self
        assert(def1 == "we2222")
        assert(kwargs == {"jada":"bada"})

    def arg_and_default(self, x, y=2):
        assert(x == 'y')
        assert(y == 'z')

    def arg_default_and_kwargs(self, x, y=2, **z):
        print x, y, z
        assert(x == 'y')
        assert(y == 'z')
        assert(z == {'z':'x'})

    def only_defaulters(self, def1="1", def2="2"):
        print "def1='%r' def2='%r'" % (def1, def2)
        assert(def1 == 'killu=tillu')
        assert(def2 == 'tillu')

    def everything(self, yks, kaks=2, *koli, **neli):
        print yks, kaks, koli, neli
        assert(yks == 'first')
        assert(kaks == 2 or kaks.startswith('second'))
        assert(not koli or all('third' == i for i in koli))
        assert(not neli or all(v.startswith('fourth') for v in neli.values()))

    def return_stuff(self):
        return (self.command, self.args, self.kwargs)

    def __str__(self):
        output = "vargs_and_kwargs()\n"
        output += "\t%12s: %r\n" % ("command", self.command)
        output += "\t%12s: %r\n" % ("args", self.args)
        output += "\t%12s: %r\n" % ("kwargs", self.kwargs)
        return output

if __name__ == "__main__":
    dl = TestKwargsLibrary()
    dl.vargs_and_kwargs("dfssffds", 333, 555, named="dasdasdasd", another="2323232")
    print dl