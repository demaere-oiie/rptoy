from mach import get_location, jitcfg, run
from rom import code, prog, DELTA
from terpval import IntBox, SeqBox, litInt, strInt
# build 'rptoy-c' via 'rpython -O jit rptoy.py'

facargs = litInt(1000)
gcdargs = SeqBox(litInt(6*9035768),
                 litInt(6*8675309))

facres = strInt(
"402387260077093773543702433923003985719374864210714632543799910429938512398629020592044208486969404800479988610197196058631666872994808558901323829669944590997424504087073759918823627727188732519779505950995276120874975462497043601418278094646496291056393887437886487337119181045825783647849977012476632889835955735432513185323958463075557409114262417474349347553428646576611667797396668820291207379143853719588249808126867838374559731746136085379534524221586593201928090878297308431392844403281231558611036976801357304216168747609675871348312025478589320767169132448426236131412508780208000261683151027341827977704784635868170164365024153691398281264810213092761244896359928705114964975419909342221566832572080821333186116811553615836546984046708975602900950537616475847728421889679646244945160765353408198901385442487984959953319101723355556602139450399736280750137837615307127761926849034352625200015888535147331611702103968175921510907788019393178114194545257223865541461062892187960223838971476088506276862967146674697562911234082439208160153780889893964518263243671616762179168909779911903754031274622289988005195444414282012187361745992642956581746628302955570299024324153181617210465832036786906117260158783520751516284225540265170483304226143974286933061690897968482590125458327168226458066526769958652682272807075781391858178889652208164348344825993266043367660176999612831860788386150279465955131156552036093988180612138558600301435694527224206344631797460594682573103790084024432438465657245014402821885252470935190620929023136493273497565513958720559654228749774011413346962715422845862377387538230483865688976461927383814900140767310446640259899490222221765904339901886018566526485061799702356193897017860040811889729918311021171229845901641921068884387121855646124960798722908519296819372388642614839657382291123125024186649353143970137428531926649875337218940694281434118520158014123344828015051399694290153483077644569099073152433278288269864602789864321139083506217095002597389863554277196742822248757586765752344220207573630569498825087968928162753848863396909959826280956121450994871701244516461260379029309120889086942028510640182154399457156805941872748998094254742173582401063677404595741785160829230135358081840096996372524230560855903700624271243416909004153690105933983835777939410970027753472000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
gcdres = litInt(6)
sumres = litInt(500500)
zero = litInt(0)

conf = {"fac":  (facargs, 8000, facres),
        "cfac": (facargs, 8000, facres),
        "sum":  (facargs, 20000, sumres),
        "csum": (facargs, 20000, sumres),
        "gcd":  (gcdargs, 160000, gcdres),
        "odd":  (facargs, 20000, zero),
        "rodd": (facargs, 20000, zero),
}

def main(argv):
    if len(argv)>2:
        print(argv[2])
        jitcfg(argv[2]) # eg "off"

    sel = argv[1] if len(argv)>1 else "fac"

    ipc = code.get(sel,len(prog)-1)
    for i in range(ipc,min(ipc+50,len(prog))):
        if DELTA<=prog[i]:
            print(get_location(i))

    ini, reps, chk = conf.get(sel,(zero,4000,zero))

    if len(argv)>3:
        reps = int(argv[3])

    for i in range(reps):
        run(ipc,ini)

    res = run(ipc,ini)
    if not isinstance(res,IntBox) or not res.eq(chk):
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
