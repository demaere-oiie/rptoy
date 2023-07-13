from rpython.rlib.rbigint import rbigint
from rpython.rlib import rarithmetic

class Box(object):
    _attrs_ = []
    len = lambda self: 1
    take = lambda self,n: self
    ekat = lambda self,n: self

class IntBox(Box):
    _attrs_ = []

class RegBox(IntBox):
    def __init__(self,val):
        self.regval = val

    ge  = lambda self, other: (self.regval >= other.regval
                               if isinstance(other,RegBox) else
                               other.intval.int_le(self.regval)
                               if isinstance(other,BigBox) else False)
    lt  = lambda self, other: (self.regval < other.regval
                               if isinstance(other,RegBox) else
                               other.intval.int_gt(self.regval)
                               if isinstance(other,BigBox) else False)
    eq  = lambda self, other: (self.regval == other.regval
                               if isinstance(other,RegBox) else
                               other.intval.int_eq(self.regval)
                               if isinstance(other,BigBox) else False)

    def add(self,other):
        if isinstance(other,RegBox):
            try: 
               res = rarithmetic.ovfcheck(self.regval + other.regval)
            except OverflowError:
               return self.add(BigBox(rbigint.fromint(other.regval)))
            return RegBox(res)
        elif isinstance(other,BigBox):
            return BigBox(other.intval.int_add(self.regval))

    def sub(self,other):
        if isinstance(other,RegBox):
            return RegBox(self.regval - other.regval)
        elif isinstance(other,BigBox):
            return BigBox(rbigint.fromint(self.regval).sub(other.intval))

    def mul(self,other):
        if isinstance(other,RegBox):
            try: 
               res = rarithmetic.ovfcheck(self.regval * other.regval)
            except OverflowError:
               return self.mul(BigBox(rbigint.fromint(other.regval)))
            return RegBox(res)
        elif isinstance(other,BigBox):
            return BigBox(other.intval.int_mul(self.regval))

    str = lambda self: str(self.regval)

class BigBox(IntBox):
    def __init__(self, val):
        self.intval = val

    ge  = lambda self, other: (self.intval.ge(other.intval)
                               if isinstance(other,BigBox) else
                               self.intval.int_ge(other.regval)
                               if isinstance(other,RegBox) else False)
    lt  = lambda self, other: (self.intval.lt(other.intval)
                               if isinstance(other,BigBox) else
                               self.intval.int_lt(other.regval)
                               if isinstance(other,RegBox) else False)
    eq  = lambda self, other: (self.intval.eq(other.intval)
                               if isinstance(other,BigBox) else
                               self.intval.int_eq(other.regval)
                               if isinstance(other,RegBox) else False)

    def add(self,other):
        if isinstance(other,BigBox):
            return BigBox(self.intval.add(other.intval))
        elif isinstance(other,RegBox):
            return BigBox(self.intval.int_add(other.regval))

    def sub(self,other):
        if isinstance(other,BigBox):
            return BigBox(self.intval.sub(other.intval))
        elif isinstance(other,RegBox):
            return BigBox(self.intval.int_sub(other.regval))

    def mul(self,other):
        if isinstance(other,BigBox):
            return BigBox(self.intval.mul(other.intval))
        elif isinstance(other,RegBox):
            return BigBox(self.intval.int_mul(other.regval))

    str = lambda self: self.intval.str()

litInt = lambda n: RegBox(n)
strInt = lambda s: BigBox(rbigint.fromstr(s))

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
