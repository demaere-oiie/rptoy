nam = """
REP COM LAM LIT MOC CUS REZ MUL RHO SUB XGE XLT HLT APP CLO REF RET TNI ADD
""".strip().split(' ')

DELTA=1000

REP,COM,LAM,LIT,MOC,CUS,REZ,MUL,RHO,\
SUB,XGE,XLT,HLT,APP,CLO,REF,RET,TNI,ADD = range(DELTA,DELTA+len(nam))

rep = lambda xs: xs+[REP, len(xs)]
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

prog = pad(400,pad(300,pad(200,pad(100,pcfac)+pfac)+pgcd)+pcsum)+psum
code = {"cfac":0, "fac":100, "gcd":200, "csum":300, "sum":400}
