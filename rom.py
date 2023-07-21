nam = """
REP COM LAM LIT MOC CUS REZ MUL RHO SUB XGE XLT HLT APP CLO REF RET TNI
ADD ALT
""".strip().split()

DELTA=1000

REP,COM,LAM,LIT,MOC,CUS,REZ,MUL,RHO,\
SUB,XGE,XLT,HLT,APP,CLO,REF,RET,TNI,\
ADD,ALT = range(DELTA,DELTA+len(nam))

rep = lambda xs: xs+[REP, len(xs)]
alt = lambda xs: [ALT, len(xs)]+xs
pad = lambda n,xs: xs + (n-len(xs))*[HLT]

# fac := (a@0,a),Rep.(n-1,n*a @ (n>0),a),(,1)
l0 = [LAM, LIT, 1, COM, 0, 1, RHO]
l1 = [LAM, MOC, 0, CUS, 1, TNI, 2, MUL, 1, 2, COM, 3, 4, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]
pfac = l0 + rep(l1) + l2 + [HLT]

# cfac := (a@0,a),Rep.(n-1,m.a @ (n>0),a ~ m.x:=n*x),(,1)
l0 = [LAM, LIT, 1, COM, 0, 1, RHO]
l1 = [LAM, MOC, 0, CUS, 1, TNI, 2, CLO, 35, APP, 4, 2, COM, 3, 5, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]
l3 = [LAM, TNI, 0, REF, 1, 1, MUL, 0, 1, RHO, RET]
pcfac = pad(35, l0 + rep(l1) + l2 + [HLT]) + l3

# gcd := (x@x,x),Rep.(x-y,y @ x,(y<x) :: x,y-x @ (x<y),y)
l0 = [LAM, MOC, 0, XLT, 1, 2, SUB, 2, 1, COM, 1, 3, RHO]
l1 = [LAM, MOC, 0, XLT, 2, 1, SUB, 1, 2, COM, 3, 2, RHO]
l2 = [LAM, MOC, 0, RHO]
pgcd = rep(rep(l0) + l1) + l2 + [HLT]

# csum := (a@0,a),Rep.(n-1,m.a @ (n>0),a ~ m.x:=n+x),(,0)
l0 = [LAM, LIT, 0, COM, 0, 1, RHO]
l1 = [LAM, MOC, 0, CUS, 1, TNI, 2, CLO, 335, APP, 4, 2, COM, 3, 5, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]
l3 = [LAM, TNI, 0, REF, 1, 1, ADD, 0, 1, RHO, RET]
pcsum = pad(35, l0 + rep(l1) + l2 + [HLT]) + l3

# sum := (a@0,a),Rep.(n-1,n+a @ (n>0),a),(,0)
l0 = [LAM, LIT, 0, COM, 0, 1, RHO]
l1 = [LAM, MOC, 0, CUS, 1, TNI, 2, ADD, 1, 2, COM, 3, 4, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]
psum = l0 + rep(l1) + l2 + [HLT]

podd = [HLT] # deprecated

# rodd := (o ~ e:=(1@0::o.(n-1)@n>0) && o:=(0@0::e.(n-1)@n>0))
l0 = [LAM, CLO, 610, CLO, 630, APP, 2, 0, RHO]
l1 = [LAM, CUS, 0, REF, 1, 2, APP, 2, 1, RHO]
l2 = [LAM, REZ, 0, LIT, 1, RHO]
l3 = [LAM, CUS, 0, REF, 1, 1, APP, 2, 1, RHO]
l4 = [LAM, REZ, 0, LIT, 0, RHO]
prodd = pad(10,l0) + pad(20,l1+alt(l2)+[RET]) + pad(20,l3+alt(l4)+[RET])

# hfac := (go.(n,1) @ n ~ go:=(a @ 0,a :: go $ n-1,n*a @ (n>0),a))
l0 = [LAM, CLO, 715, LIT, 1, COM, 0, 2, APP, 1, 3, RHO]
l1 = [LAM, MOC, 0, CUS, 1, TNI, 2, MUL, 1, 2, COM, 3, 4,
      REF, 1, 1, APP, 6, 5, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]
phfac = pad(15, l0) + l1+alt(l2)+[RET]

# hsum := (go.(n,0) @ n ~ go:=(a @ 0,a :: go $ n-1,n+a @ (n>0),a))
l0 = [LAM, CLO, 815, LIT, 0, COM, 0, 2, APP, 1, 3, RHO]
l1 = [LAM, MOC, 0, CUS, 1, TNI, 2, ADD, 1, 2, COM, 3, 4,
      REF, 1, 1, APP, 6, 5, RHO]
l2 = [LAM, MOC, 0, REZ, 1, RHO]
phsum = pad(15, l0) + l1+alt(l2)+[RET]

# hgcd := (go ~ go:=(x@x,x :: go $ x-y,y @ (x>y),y :: go $ x,y-x @ x,(y>x)))
l0 = [LAM, CLO, 910, APP, 1, 0, RHO]
l1 = [LAM, MOC, 0, XLT, 1, 2, SUB, 2, 1, COM, 1, 3, REF, 1, 1, APP, 5, 4, RHO]
l2 = [LAM, MOC, 0, XLT, 2, 1, SUB, 1, 2, COM, 3, 2, REF, 1, 1, APP, 5, 4, RHO]
l3 = [LAM, MOC, 0, RHO]
phgcd = pad(10,l0) + l1+alt(l2 + alt(l3))+[RET]

prog = [r for c in [pcfac,pfac,pgcd,pcsum,psum,podd,prodd,phfac,phsum,phgcd]
          for r in pad(100,c)]
code = {"cfac":0, "fac":100, "gcd":200, "csum":300, "sum":400,
        "XXXX":500, "odd":600, "hfac":700, "hsum":800, "hgcd":900}
