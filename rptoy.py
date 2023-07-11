from rpython.rlib import jit
from rpython.rlib.rbigint import rbigint
# build 'rptoy-c' via 'rpython -O jit rptoy.py'

################################################################################

nam = """
REP COM LAM LIT MOC CUS REZ MUL RHO SUB XGE XLT HLT APP CLO REF RET TNI ADD
""".strip().split(' ')

DELTA=1000

REP,COM,LAM,LIT,MOC,CUS,REZ,MUL,RHO,\
SUB,XGE,XLT,HLT,APP,CLO,REF,RET,TNI,ADD = range(DELTA,DELTA+len(nam))

rep = lambda xs: xs+[REP, len(xs)]
pad = lambda n,xs: xs + (n-len(xs))*[HLT]

l0 = [LAM, LIT, 1, COM, 0, 1, RHO]
l1 = [LAM, MOC, 0, CUS, 1, TNI, 2, MUL, 1, 2, COM, 3, 4, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]

pfac = l0 + rep(l1) + l2 + [HLT]

l0 = [LAM, LIT, 1, COM, 0, 1, RHO]
l1 = [LAM, MOC, 0, CUS, 1, TNI, 2, CLO, 35, APP, 4, 2, COM, 3, 5, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]
l3 = [LAM, TNI, 0, REF, 1, 1, MUL, 0, 1, RHO, RET]

pcfac = pad(35, l0 + rep(l1) + l2 + [HLT]) + l3

l0 = [LAM, MOC, 0, XLT, 1, 2, SUB, 2, 1, COM, 1, 3, RHO]
l1 = [LAM, MOC, 0, XLT, 2, 1, SUB, 1, 2, COM, 3, 2, RHO]
l2 = [LAM, MOC, 0, RHO]

pgcd = rep(rep(l0) + l1) + l2 + [HLT]

l0 = [LAM, LIT, 0, COM, 0, 1, RHO]
l1 = [LAM, MOC, 0, CUS, 1, TNI, 2, CLO, 335, APP, 4, 2, COM, 3, 5, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]
l3 = [LAM, TNI, 0, REF, 1, 1, ADD, 0, 1, RHO, RET]

pcsum = pad(35, l0 + rep(l1) + l2 + [HLT]) + l3

l0 = [LAM, LIT, 0, COM, 0, 1, RHO]
l1 = [LAM, MOC, 0, CUS, 1, TNI, 2, ADD, 1, 2, COM, 3, 4, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]

psum = l0 + rep(l1) + l2 + [HLT]

prog = pad(400,pad(300,pad(200,pad(100,pcfac)+pfac)+pgcd)+pcsum)+psum
code = {"cfac":0, "fac":100, "gcd":200, "csum":300, "sum":400}

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

class ListBox(Box):
    def __init__(self, val):
        self.vlen = val[0].len() + val[1].len()
        self.head = val[0]
        self.tail = val[1]

    def split(self, frame):
        h = self.vlen//2
        frame.append(self.take(h))
        frame.append(self.ekat(self.vlen-h))

    len = lambda self: self.vlen

    def take(self,n):
        if n==self.vlen:         return self
        elif n<=self.head.len(): return self.head.take(n)
        else:                    return ListBox((self.head,
                                     self.tail.take(n-self.head.len())))

    def ekat(self,n):
        if n==self.vlen:         return self
        elif n<=self.tail.len(): return self.tail.ekat(n)
        else:                    return ListBox((
                                     self.head.ekat(n-self.tail.len()),
                                     self.tail))

    str = lambda self: "<List>"

class CloBox(Box):
    def __init__(self, val):
        self.cloval = val

    len = lambda self: 1
    str = lambda self: "<Closure>"


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

class Stack(object):
    def __init__(self, ctx, pc, link, prev):
        self.ctx = ctx
        self.pc = pc
        self.link = link
        self.prev = prev

    pop = lambda self: (self.ctx, self.pc, self.link, self.prev)

################################################################################

def run(ipc,ini):
    pc = ipc
    ctx  = Ctx(ini)
    stack = None
    link = None

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
            x = ctx[prog[pc]]
            pc = pc+1
            y = ctx[prog[pc]]
            ctx.append(ListBox((x,y)))
        elif op == LAM: # start a frame, cf RHO
            ctx.lam()
        elif op == LIT: # int literal
            pc = pc+1
            ctx.append(IntBox(rbigint.fromint(prog[pc])))
        elif op == MOC: # list deconstruction, cf COM
            pc = pc+1
            x = ctx[prog[pc]]
            if not isinstance(x,ListBox): pc=fail(pc)
            else: x.split(ctx)
        elif op == CUS: # nat deconstruction S(x)
            pc = pc+1
            x = ctx[prog[pc]]
            if not isinstance(x,IntBox): pc=fail(pc)
            elif not x.intval.int_ge(1): pc=fail(pc)
            else: ctx.append(IntBox(x.intval.int_sub(1)))
        elif op == REZ: # nat deconstruction Z
            pc = pc+1
            x = ctx[prog[pc]]
            if not isinstance(x,IntBox): pc=fail(pc)
            elif not x.intval.int_lt(1): pc=fail(pc)
        elif op == TNI: # any int
            pc = pc+1
            x = ctx[prog[pc]]
            if not isinstance(x,IntBox): pc=fail(pc)
        elif op == MUL:
            pc = pc+1
            x = ctx[prog[pc]]
            pc = pc+1
            y = ctx[prog[pc]]
            assert isinstance(x,IntBox)
            assert isinstance(y,IntBox)
            ctx.append(x.mul(y))
        elif op == RHO: # end a frame, cf LAM
            ctx.rho()
        elif op == ADD:
            pc = pc+1
            x = ctx[prog[pc]]
            pc = pc+1
            y = ctx[prog[pc]]
            assert isinstance(x,IntBox)
            assert isinstance(y,IntBox)
            ctx.append(x.add(y))
        elif op == SUB:
            pc = pc+1
            x = ctx[prog[pc]]
            pc = pc+1
            y = ctx[prog[pc]]
            assert isinstance(x,IntBox)
            assert isinstance(y,IntBox)
            ctx.append(x.sub(y))
        elif op == XGE:
            pc = pc+1
            x = ctx[prog[pc]]
            pc = pc+1
            y = ctx[prog[pc]]
            if (not isinstance(x,IntBox) or
                not isinstance(y,IntBox) or
                not x.ge(y)): pc=fail(pc)
        elif op == XLT:
            pc = pc+1
            x = ctx[prog[pc]]
            pc = pc+1
            y = ctx[prog[pc]]
            if (not isinstance(x,IntBox) or
                not isinstance(y,IntBox) or
                not x.lt(y)): pc=fail(pc)
        elif op == APP:
            pc = pc+1
            x = ctx[prog[pc]]
            pc = pc+1
            y = ctx[prog[pc]]
            stack = Stack(ctx, pc, link, stack)
            assert isinstance(x,CloBox)
            pc, link = x.cloval
            ctx = Ctx(y)
            continue
        elif op == CLO:
            pc = pc+1
            u = prog[pc]
            ctx.append(CloBox((u,Link(link,ctx.frame))))
        elif op == REF:
            pc = pc+1
            u = prog[pc]
            pc = pc+1
            v = prog[pc]
            assert isinstance(link,Link)
            ctx.append(link.getref(u)[v])
        elif op == RET:
            x = ctx.state
            assert stack is not None
            ctx,pc,link,stack = stack.pop()
            ctx.append(x)
        elif op == HLT: # end run
            break
        pc = pc+1
    return ctx.state

################################################################################

facargs = IntBox(rbigint.fromint(1000))
gcdargs = ListBox([IntBox(rbigint.fromint(6*9035768)),
                   IntBox(rbigint.fromint(6*8675309))])

facres = IntBox(rbigint.fromstr(
"402387260077093773543702433923003985719374864210714632543799910429938512398629020592044208486969404800479988610197196058631666872994808558901323829669944590997424504087073759918823627727188732519779505950995276120874975462497043601418278094646496291056393887437886487337119181045825783647849977012476632889835955735432513185323958463075557409114262417474349347553428646576611667797396668820291207379143853719588249808126867838374559731746136085379534524221586593201928090878297308431392844403281231558611036976801357304216168747609675871348312025478589320767169132448426236131412508780208000261683151027341827977704784635868170164365024153691398281264810213092761244896359928705114964975419909342221566832572080821333186116811553615836546984046708975602900950537616475847728421889679646244945160765353408198901385442487984959953319101723355556602139450399736280750137837615307127761926849034352625200015888535147331611702103968175921510907788019393178114194545257223865541461062892187960223838971476088506276862967146674697562911234082439208160153780889893964518263243671616762179168909779911903754031274622289988005195444414282012187361745992642956581746628302955570299024324153181617210465832036786906117260158783520751516284225540265170483304226143974286933061690897968482590125458327168226458066526769958652682272807075781391858178889652208164348344825993266043367660176999612831860788386150279465955131156552036093988180612138558600301435694527224206344631797460594682573103790084024432438465657245014402821885252470935190620929023136493273497565513958720559654228749774011413346962715422845862377387538230483865688976461927383814900140767310446640259899490222221765904339901886018566526485061799702356193897017860040811889729918311021171229845901641921068884387121855646124960798722908519296819372388642614839657382291123125024186649353143970137428531926649875337218940694281434118520158014123344828015051399694290153483077644569099073152433278288269864602789864321139083506217095002597389863554277196742822248757586765752344220207573630569498825087968928162753848863396909959826280956121450994871701244516461260379029309120889086942028510640182154399457156805941872748998094254742173582401063677404595741785160829230135358081840096996372524230560855903700624271243416909004153690105933983835777939410970027753472000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"))
gcdres = IntBox(rbigint.fromint(6))
sumres = IntBox(rbigint.fromint(500500))

conf = {"fac":  (facargs, 800, facres),
        "cfac": (facargs, 800, facres),
        "sum":  (facargs, 2000, sumres),
        "csum": (facargs, 2000, sumres),
        "gcd":  (gcdargs, 16000, gcdres)}

def main(argv):
    if len(argv)>2:
        print(argv[2])
        jit.set_user_param(jitdriver, argv[2]) # eg "off"

    sel = argv[1] if len(argv)>1 else "fac"

    ipc = code.get(sel,len(prog)-1)
    for i in range(ipc,min(ipc+50,len(prog))):
        if DELTA<=prog[i]:
            print(get_location(i))

    zero = IntBox(rbigint.fromint(0))
    ini, reps, chk = conf.get(sel,(zero,400,zero))

    for i in range(reps): run(ipc,ini)

    res = run(ipc,ini)
    if not isinstance(res,IntBox) or not res.intval.eq(chk.intval):
        print("ERROR:")
        print(res.str())
        print("was not equal to:")
        print(chk.str())
        return 1

    return 0

target = lambda *args: main

if __name__=="__main__":
    import sys
    main(sys.argv)
