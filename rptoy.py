from rpython.rlib import jit
from rpython.rlib.rbigint import rbigint
# build 'rptoy-c' via 'rpython -O jit rptoy.py'

################################################################################

nam = """
REP COM LAM LIT MOC CUS REZ MUL RHO SUB XGE XLT HLT APP CLO REF RET
""".strip().split(' ')

DELTA=1000

REP,COM,LAM,LIT,MOC,CUS,REZ,MUL,RHO,\
SUB,XGE,XLT,HLT,APP,CLO,REF,RET = range(DELTA,DELTA+len(nam))

rep = lambda xs: xs+[REP, len(xs)]
pad = lambda n,xs: xs + (n-len(xs))*[HLT]

l0 = [LAM, LIT, 1, COM, 0, 1, RHO]
l1 = [LAM, MOC, 0, CUS, 1, MUL, 1, 2, COM, 3, 4, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]

pfac = l0 + rep(l1) + l2 + [HLT]

l0 = [LAM, LIT, 1, COM, 0, 1, RHO]
l1 = [LAM, MOC, 0, CUS, 1, CLO, 40, APP, 4, 2, COM, 3, 5, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]
l3 = [LAM, REF, 1, 1, MUL, 0, 1, RHO, RET]

pcfac = pad(40, l0 + rep(l1) + l2 + [HLT]) + l3

l0 = [LAM, MOC, 0, XLT, 1, 2, SUB, 2, 1, COM, 1, 3, RHO]
l1 = [LAM, MOC, 0, XLT, 2, 1, SUB, 1, 2, COM, 3, 2, RHO]
l2 = [LAM, MOC, 0, RHO]

pgcd = rep(rep(l0) + l1) + l2 + [HLT]

prog = pad(200,pad(100,pcfac)+pfac)+pgcd
code = {"cfac":0, "fac":100, "gcd":200}

################################################################################
get_location = lambda pc: "%d: %s" % (pc,
        str(prog[pc]) if prog[pc]<DELTA else
        nam[prog[pc]-DELTA]) + argp(pc+1)
argp = lambda pc: ("" if len(prog)<=pc or not prog[pc]<DELTA else
                   " "+str(prog[pc])+argp(pc+1))

jitdriver = jit.JitDriver(greens=['pc'], reds=['ctx','stack','link'],
                          get_printable_location=get_location)
################################################################################

class Box(object):
    pass

class IntBox(Box):
    def __init__(self, val):
        self.intval = val

    ge  = lambda self, other: self.intval.ge(other.intval)
    lt  = lambda self, other: self.intval.lt(other.intval)
    sub = lambda self, other: IntBox(self.intval.sub(other.intval))
    mul = lambda self, other: IntBox(self.intval.mul(other.intval))

    str = lambda self: self.intval.str()

class ListBox(Box):
    def __init__(self, val):
        self.listval = val

    def split(self, frame):
        xs = self.listval
        h = len(xs)//2
        frame.append(dn(xs[:h]))
        frame.append(dn(xs[h:]))

    str = lambda self: "<List>"

class CloBox(Box):
    def __init__(self, val):
        self.cloval = val

    str = lambda self: "<Closure>"

def up(obj):
    return obj.listval if isinstance(obj,ListBox) else [obj]

def dn(obj):
    return ListBox(obj) if len(obj)!=1 else obj[0]

################################################################################

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
    def __init__(self, val):
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

################################################################################

def run(ipc,ini):
    # initialisation mostly to force typing; is there a better way?
    pc = ipc
    op = HLT
    ctx  = Ctx(ini)
    flag = False
    x = 0
    y = 0
    stack = [(Ctx(None),0,None)]
    link = Link(None, None)

    def fail(pc):
        while prog[pc] != RHO:
            pc = pc+1
        return pc

    while True:
        jitdriver.jit_merge_point(pc=pc,ctx=ctx,stack=stack,link=link)
        op = prog[pc]
        if op == REP: # repeat on success
            if ctx.flag:
                pc = pc - prog[pc+1]
                jitdriver.can_enter_jit(pc=pc,ctx=ctx,stack=stack,link=link)
                continue
            pc = pc+1
        elif op == COM: # list construction, cf MOC
            pc = pc+1
            x = prog[pc]
            pc = pc+1
            y = prog[pc]
            ctx.append(dn(up(ctx[x])+up(ctx[y])))
        elif op == LAM: # start a frame, cf RHO
            ctx.lam()
        elif op == LIT: # int literal
            pc = pc+1
            ctx.append(IntBox(rbigint.fromint(prog[pc])))
        elif op == MOC: # list deconstruction, cf COM
            pc = pc+1
            x = prog[pc]
            if not isinstance(ctx[x],ListBox): pc=fail(pc)
            elif len(ctx[x].listval)<2: pc=fail(pc)
            else: ctx[x].split(ctx)
        elif op == CUS: # nat deconstruction S(x)
            pc = pc+1
            x = prog[pc]
            if not isinstance(ctx[x],IntBox): pc=fail(pc)
            elif not ctx[x].intval.ge(rbigint.fromint(1)): pc=fail(pc)
            else: ctx.append(IntBox(ctx[x].intval.int_sub(1)))
        elif op == REZ: # nat deconstruction Z
            pc = pc+1
            x = prog[pc]
            if not isinstance(ctx[x],IntBox): pc=fail(pc)
            elif not ctx[x].intval.int_lt(1): pc=fail(pc)
        elif op == MUL:
            pc = pc+1
            x = prog[pc]
            pc = pc+1
            y = prog[pc]
            ctx.append(ctx[x].mul(ctx[y]))
        elif op == RHO: # end a ctx, cf LAM
            ctx.rho()
        elif op == SUB:
            pc = pc+1
            x = prog[pc]
            pc = pc+1
            y = prog[pc]
            ctx.append(ctx[x].sub(ctx[y]))
        elif op == XGE:
            pc = pc+1
            x = prog[pc]
            pc = pc+1
            y = prog[pc]
            if not isinstance(ctx[x],IntBox): pc=fail(pc)
            if not isinstance(ctx[y],IntBox): pc=fail(pc)
            if not ctx[x].ge(ctx[y]): pc=fail(pc)
        elif op == XLT:
            pc = pc+1
            x = prog[pc]
            pc = pc+1
            y = prog[pc]
            if not isinstance(ctx[x],IntBox): pc=fail(pc)
            if not isinstance(ctx[y],IntBox): pc=fail(pc)
            if not ctx[x].lt(ctx[y]): pc=fail(pc)
        elif op == APP:
            pc = pc+1
            x = prog[pc]
            pc = pc+1
            y = prog[pc]
            stack.append((ctx, pc, link))
            pc, link = ctx[x].cloval
            ctx = Ctx(ctx[y])
            continue
        elif op == CLO:
            pc = pc+1
            x = prog[pc]
            ctx.append(CloBox((x,Link(link,ctx.frame))))
        elif op == REF:
            pc = pc+1
            x = prog[pc]
            pc = pc+1
            y = prog[pc]
            ctx.append(link.getref(x)[y])
        elif op == RET:
            rval = ctx.state
            ctx,pc,link = stack.pop()
            ctx.append(rval)
            flag = False
        elif op == HLT: # end run
            break
        pc = pc+1
    return ctx.state

################################################################################

facargs = IntBox(rbigint.fromint(1000))
gcdargs = ListBox([IntBox(rbigint.fromint(6*9035768)),
                   IntBox(rbigint.fromint(6*8675309))])

conf = {"fac":  (facargs, 200),
        "cfac": (facargs, 200),
        "gcd":  (gcdargs, 2000)}

def main(argv):
    if len(argv)>2:
        print(argv[2])
        jit.set_user_param(jitdriver, argv[2]) # eg "off"

    sel = argv[1] if len(argv)>1 else "fac"

    ipc = code.get(sel,len(prog)-1)
    for i in range(ipc,min(ipc+50,len(prog))):
        if DELTA<=prog[i]:
            print(get_location(i))

    ini, reps = conf.get(sel,(IntBox(rbigint.fromint(0)),200))

    for i in range(reps): run(ipc,ini)
    print(run(ipc,ini).str())
    return 0

target = lambda *args: main

if __name__=="__main__":
    import sys
    main(sys.argv)
