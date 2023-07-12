from rpython.rlib import jit

class Frame(object):
    def __init__(self):
        self.frame = [None, None, None, None, None, None, None, None]
        self.fp = 0

    def append(self, val):
        assert 0<=self.fp
        self.frame[self.fp] = val
        self.fp += 1

    __getitem__ = lambda self, key: self.frame[abs(key)]
    final = lambda self: self.frame[abs(self.fp-1)]

class Ctx(object):
    _virtualizable_ = ['state','frame','flag']
    def __init__(self, val):
        self = jit.hint(self, access_directly=True, fresh_virtualizable=True)
        self.state = val
        self.frame = None
        self.flag = False

    def lam(self):
        self.frame = Frame()
        self.append(self.state)
        self.flag = False

    def rho(self):
        self.state = self.frame.final()
        self.frame = None
        self.flag = True
        
    def append(self, val):
        self.frame.append(val)

    __getitem__ = lambda self, key: self.frame[key]

class Link(object):
    def __init__(self, old, frame):
         self.olink = old
         self.frame = frame

    getref = lambda self,x: self.frame if x==1 else self.olink.getref(x-1)

class Stack(object):
    def __init__(self, ctx, pc, link, prev):
        self.ctx = ctx
        self.pc = pc
        self.link = link
        self.prev = prev

    pop = lambda self: (self.ctx, self.pc, self.link, self.prev)
