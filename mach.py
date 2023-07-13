from rom import DELTA
from rom import REP,COM,LAM,LIT,MOC,CUS,REZ,MUL,RHO
from rom import SUB,XGE,XLT,HLT,APP,CLO,REF,RET,TNI,ADD
from rom import nam, prog
from rpython.rlib import jit

from machval import Ctx, Link, Stack
from terpval import CloBox, IntBox, SeqBox, litInt, RegBox

get_location = lambda pc: "%d: %s" % (pc,
        str(prog[pc]) if prog[pc]<DELTA else
        nam[prog[pc]-DELTA]) + argp(pc+1)
argp = lambda pc: ("" if len(prog)<=pc or not prog[pc]<DELTA else
                   " "+str(prog[pc])+argp(pc+1))

jitdriver = jit.JitDriver(greens=['pc'], reds=['ctx','stack','link'],
                          virtualizables=['ctx'],
                          get_printable_location=get_location)

jitcfg = lambda s: jit.set_user_param(jitdriver, s)

@jit.elidable
def fail(pc):
        while prog[pc] != RHO:
            pc = pc+1
        return pc

def run(ipc,ini):
    pc = ipc
    ctx  = Ctx(ini)
    stack = None
    link = None

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
            ctx.append(SeqBox(x,y))
        elif op == LAM: # start a frame, cf RHO
            ctx.lam()
        elif op == LIT: # int literal
            pc = pc+1
            ctx.append(litInt(prog[pc]))
        elif op == MOC: # list deconstruction, cf COM
            pc = pc+1
            x = ctx[prog[pc]]
            if not isinstance(x,SeqBox): pc=fail(pc)
            else: x.split(ctx)
        elif op == CUS: # nat deconstruction S(x)
            pc = pc+1
            x = ctx[prog[pc]]
            if not isinstance(x,IntBox): pc=fail(pc)
            elif not x.ge(litInt(1)): pc=fail(pc)
            else: ctx.append(x.sub(litInt(1)))
        elif op == REZ: # nat deconstruction Z
            pc = pc+1
            x = ctx[prog[pc]]
            if not isinstance(x,IntBox): pc=fail(pc)
            elif not x.lt(litInt(1)): pc=fail(pc)
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
