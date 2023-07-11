from rpython.rlib.rbigint import rbigint

class Box(object):
    _attrs_ = []
    len = lambda self: 1
    take = lambda self,n: self
    ekat = lambda self,n: self

class IntBox(Box):
    def __init__(self, val):
        self.intval = val

    ge  = lambda self, other: self.intval.ge(other.intval)
    lt  = lambda self, other: self.intval.lt(other.intval)
    add = lambda self, other: IntBox(self.intval.add(other.intval))
    sub = lambda self, other: IntBox(self.intval.sub(other.intval))
    mul = lambda self, other: IntBox(self.intval.mul(other.intval))

    str = lambda self: self.intval.str()

litInt = lambda n: IntBox(rbigint.fromint(n))
strInt = lambda s: IntBox(rbigint.fromstr(s))

class SeqBox(Box):
    def __init__(self, hd, tl):
        self.vlen = hd.len() + tl.len()
        self.head = hd
        self.tail = tl

    def split(self, frame):
        h = self.vlen//2
        frame.append(self.take(h))
        frame.append(self.ekat(self.vlen-h))

    len = lambda self: self.vlen

    def take(self,n):
        if n==self.vlen:         return self
        elif n<=self.head.len(): return self.head.take(n)
        else:                    return SeqBox(self.head,
                                     self.tail.take(n-self.head.len()))

    def ekat(self,n):
        if n==self.vlen:         return self
        elif n<=self.tail.len(): return self.tail.ekat(n)
        else:                    return SeqBox(
                                     self.head.ekat(n-self.tail.len()),
                                     self.tail)

    str = lambda self: "<List>"

class CloBox(Box):
    def __init__(self, val):
        self.cloval = val

    str = lambda self: "<Closure>"
