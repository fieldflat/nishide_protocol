import math
import random
import sympy


# ===========
# Constants
# ===========
# BIT = 32
# MOD_P = 2**BIT - 5
BIT = 64
LAMBDA = 8
MOD_P = 2**BIT - 59
MAX_INTEGER = 2**(2*BIT) - 1
BEAVERS = {"P1": [1, 2, 13], "P2": [2, 5, 29], "P3": [4, 1, 14]}
SHARE_OF_ONE = {"P1": 1, "P2": 0, "P3": 0}
INVERSE_OF_TWO = pow(2, -1, MOD_P)


# =======================
# util methods
# =======================
def is_range(x, min, max):
    if (min <= x) and (x < max):
        return True
    return False


def is_overflow(x):
    if (x > MAX_INTEGER) or (x < 0):
        return True
    return False


def modulo(x, p):
    if is_overflow(x):
        print("[Error] oveflow happens.")
        exit(1)
    return x % p


def add(x: int, y: int):
    if not (is_range(x, 0, MOD_P) and is_range(y, 0, MOD_P)):
        print("[Error] invalid range. (x, y) = ({0}, {1})".format(x, y))
        exit(1)

    ret = x + y
    if is_overflow(ret):
        print("[Error] oveflow happens.")
        exit(1)
    return modulo(ret, MOD_P)


def sub(x: int, y: int):
    if not (is_range(x, 0, MOD_P) and is_range(y, 0, MOD_P)):
        print("[Error] invalid range. (x, y) = ({0}, {1})".format(x, y))
        exit(1)

    if x < y:
        ret = (x + MOD_P - y)
    else:
        ret = x - y
    return modulo(ret, MOD_P)


def mult(x: int, y: int):
    if not (is_range(x, 0, MOD_P) and is_range(y, 0, MOD_P)):
        print("[Error] invalid range. (x, y) = ({0}, {1})".format(x, y))
        exit(1)

    ret = x * y
    if is_overflow(ret):
        print("[Error] oveflow happens.")
        exit(1)
    return modulo(ret, MOD_P)


def div(x: int, y: int):
    if not (is_range(x, 0, MOD_P) and is_range(y, 0, MOD_P)):
        print("[Error] invalid range.")
        exit(1)

    ret = x // y
    if is_overflow(ret):
        print("[Error] oveflow happens.")
        exit(1)
    return modulo(ret, MOD_P)


def share_mult(x1, y1, x2, y2, x3, y3):
    share_d1 = sub(x1, BEAVERS.get("P1")[0])
    share_e1 = sub(y1, BEAVERS.get("P1")[1])
    share_d2 = sub(x2, BEAVERS.get("P2")[0])
    share_e2 = sub(y2, BEAVERS.get("P2")[1])
    share_d3 = sub(x3, BEAVERS.get("P3")[0])
    share_e3 = sub(y3, BEAVERS.get("P3")[1])
    d = restore(share_d1, share_d2, share_d3)
    e = restore(share_e1, share_e2, share_e3)
    share1 = add(mult(e, BEAVERS.get("P1")[0]), add(
        mult(d, BEAVERS.get("P1")[1]), add(BEAVERS.get("P1")[2], mult(d, e))))
    share2 = add(mult(e, BEAVERS.get("P2")[0]), add(
        mult(d, BEAVERS.get("P2")[1]), add(BEAVERS.get("P2")[2], 0)))
    share3 = add(mult(e, BEAVERS.get("P3")[0]), add(
        mult(d, BEAVERS.get("P3")[1]), add(BEAVERS.get("P3")[2], 0)))
    return share1, share2, share3


# =======================
# sub protocols
# =======================
def sub_rns():  # test: ok
    share_r1 = random.randint(1, MOD_P)
    share_r2 = random.randint(1, MOD_P)
    share_r3 = random.randint(1, MOD_P)
    return share_r1, share_r2, share_r3


def sub_rbs():  # test: ok
    while True:
        # rns
        share_r1, share_r2, share_r3 = sub_rns()
        share_r2_1, share_r2_2, share_r2_3 = share_mult(
            share_r1, share_r1, share_r2, share_r2, share_r3, share_r3)
        r2 = restore(share_r2_1, share_r2_2, share_r2_3)

        r_dash = sympy.sqrt_mod(r2, MOD_P)
        r_dash_inv = pow(r_dash, -1, MOD_P)

        share1 = mult(INVERSE_OF_TWO, add(mult(r_dash_inv, share_r1), 1))
        share2 = mult(INVERSE_OF_TWO, add(mult(r_dash_inv, share_r2), 0))
        share3 = mult(INVERSE_OF_TWO, add(mult(r_dash_inv, share_r3), 0))

        return share1, share2, share3


def sub_rbvs(): # test: ok
    share1_list = []
    share2_list = []
    share3_list = []
    for _ in range(BIT):
        s1, s2, s3 = sub_rbs()
        share1_list.append(s1)
        share2_list.append(s2)
        share3_list.append(s3)

    #
    # TODO: r < p チェックをここで行う
    #
    return share1_list, share2_list, share3_list


def sub_unbounded_fan_in_or(bit_share_list1, bit_share_list2, bit_share_list3): # test: ok
    # 1: ok
    A1_share, A2_share, A3_share = 1, 0, 0
    for i in bit_share_list1:
        A1_share = add(A1_share, i)
    for i in bit_share_list2:
        A2_share = add(A2_share, i)
    for i in bit_share_list3:
        A3_share = add(A3_share, i)

    # 3
    b1_share_list = []
    b1_dash_share_list = []
    b2_share_list = []
    b2_dash_share_list = []
    b3_share_list = []
    b3_dash_share_list = []
    for i in range(0, BIT):
        share_r1, share_r2, share_r3 = sub_rns()
        share_dash_r1, share_dash_r2, share_dash_r3 = sub_rns()
        b1_share_list.append(share_r1)
        b2_share_list.append(share_r2)
        b3_share_list.append(share_r3)
        b1_dash_share_list.append(share_dash_r1)
        b2_dash_share_list.append(share_dash_r2)
        b3_dash_share_list.append(share_dash_r3)

    # 4
    B1_share_list = []
    B2_share_list = []
    B3_share_list = []
    for i in range(0, BIT):
        share_1, share_2, share_3 = share_mult(
            b1_share_list[i], b1_dash_share_list[i], b2_share_list[i],
            b2_dash_share_list[i], b3_share_list[i], b3_dash_share_list[i])
        B1_share_list.append(share_1)
        B2_share_list.append(share_2)
        B3_share_list.append(share_3)

    B_list = []
    for i in range(0, BIT):
        ret = add(B1_share_list[i], add(B2_share_list[i], B3_share_list[i]))
        B_list.append(ret)

    # 5
    b1_inverse_share_list = []
    b2_inverse_share_list = []
    b3_inverse_share_list = []
    for i in range(0, BIT):
        b1_inverse_share_list.append(
            mult(pow(B_list[i], -1, MOD_P), b1_dash_share_list[i]))
        b2_inverse_share_list.append(
            mult(pow(B_list[i], -1, MOD_P), b2_dash_share_list[i]))
        b3_inverse_share_list.append(
            mult(pow(B_list[i], -1, MOD_P), b3_dash_share_list[i]))

    # 6
    # c1_share_list = []
    # c2_share_list = []
    # c3_share_list = []
    c_list = []
    for i in range(0, BIT):
        if i == 0:
            share_1, share_2, share_3 = share_mult(
                A1_share, b1_inverse_share_list[i],
                A2_share, b2_inverse_share_list[i],
                A3_share, b3_inverse_share_list[i]
            )
            c_list.append(restore(share_1, share_2, share_3))
        else:
            share_1, share_2, share_3 = share_mult(
                A1_share, b1_inverse_share_list[i],
                A2_share, b2_inverse_share_list[i],
                A3_share, b3_inverse_share_list[i]
            )
            share_1, share_2, share_3 = share_mult(
                share_1, b1_share_list[i-1],
                share_2, b2_share_list[i-1],
                share_3, b3_share_list[i-1]
            )
            c_list.append(restore(share_1, share_2, share_3))

    A1_exp_list = []
    A2_exp_list = []
    A3_exp_list = []
    t = 1
    for i in range(0, BIT):
        t = mult(t, c_list[i])
        A1_exp_list.append(mult(t, b1_share_list[i]))
        A2_exp_list.append(mult(t, b2_share_list[i]))
        A3_exp_list.append(mult(t, b3_share_list[i]))

    # ラグランジュの未定係数法
    or_list = [
        18446744073709551493,
        2575104960981055254,
        4007652756006865783,
        4100635666949508952,
        13520771370602560384,
        10644542489970931539,
        13748537863183121296,
        11359914866391222416,
        11247219807349180267,
        10960075435459066463,
        16764588636202349672,
        17506652363315270202,
        16166875542546532309,
        3964617125041583173,
        11719255904316824165,
        10424936898019828672,
        4205127743406738449,
        14520034406506226582,
        13839012095455519695,
        10500139574289659412,
        2962336181382223452,
        6767675871271430215,
        6933421926280334339,
        15958841553693851655,
        15160740279984758829,
        7422142630459751295,
        8493480566397125402,
        5197722549818600602,
        14735780618044279429,
        1253747699690153233,
        16331314050017923346,
        8939522708637072316,
        14886963398089785966,
        9073751420990236602,
        12505410719513991034,
        2125245660187079351,
        15846075763828250700,
        3886182126918060030,
        8108428213219044342,
        7230779232974847667,
        16872135629383927467,
        6378144199063646497,
        17663587804867607672,
        16148746862917335565,
        15537620600452524460,
        5258026759045415754,
        13903054235566673560,
        13960238641761739087,
        17636644537631434137,
        14478303024279957496,
        2874963986830092253,
        3027861925099033411,
        3827102190137661457,
        12528878074288803348,
        5215393447045447612,
        9586533887964671917,
        3356091034157294274,
        2902984712153508625,
        6333090465997358509,
        9996528576620247823,
        11806089667835996467,
        15792408873328964335,
        14951514151164516184,
        2230240327554514938,
        17774600287293087221,
    ]

    share_f1, share_f2, share_f3 = 0, 0, 0
    for index, value in enumerate(or_list):
        if index == 0:
            share_f1 = add(share_f1, value)
        else:
            share_f1 = add(share_f1, mult(value, A1_exp_list[index-1]))
            share_f2 = add(share_f2, mult(value, A2_exp_list[index-1]))
            share_f3 = add(share_f3, mult(value, A3_exp_list[index-1]))

    return share_f1, share_f2, share_f3


def sub_unbounded_fan_in_and(bit_share_list1, bit_share_list2, bit_share_list3): # test: ok
    # 1: ok
    A1_share, A2_share, A3_share = 1, 0, 0
    for i in bit_share_list1:
        A1_share = add(A1_share, i)
    for i in bit_share_list2:
        A2_share = add(A2_share, i)
    for i in bit_share_list3:
        A3_share = add(A3_share, i)

    # 3
    b1_share_list = []
    b1_dash_share_list = []
    b2_share_list = []
    b2_dash_share_list = []
    b3_share_list = []
    b3_dash_share_list = []
    for i in range(0, BIT):
        share_r1, share_r2, share_r3 = sub_rns()
        share_dash_r1, share_dash_r2, share_dash_r3 = sub_rns()
        b1_share_list.append(share_r1)
        b2_share_list.append(share_r2)
        b3_share_list.append(share_r3)
        b1_dash_share_list.append(share_dash_r1)
        b2_dash_share_list.append(share_dash_r2)
        b3_dash_share_list.append(share_dash_r3)

    # 4
    B1_share_list = []
    B2_share_list = []
    B3_share_list = []
    for i in range(0, BIT):
        share_1, share_2, share_3 = share_mult(
            b1_share_list[i], b1_dash_share_list[i], b2_share_list[i],
            b2_dash_share_list[i], b3_share_list[i], b3_dash_share_list[i])
        B1_share_list.append(share_1)
        B2_share_list.append(share_2)
        B3_share_list.append(share_3)

    B_list = []
    for i in range(0, BIT):
        ret = add(B1_share_list[i], add(B2_share_list[i], B3_share_list[i]))
        B_list.append(ret)

    # 5
    b1_inverse_share_list = []
    b2_inverse_share_list = []
    b3_inverse_share_list = []
    for i in range(0, BIT):
        b1_inverse_share_list.append(
            mult(pow(B_list[i], -1, MOD_P), b1_dash_share_list[i]))
        b2_inverse_share_list.append(
            mult(pow(B_list[i], -1, MOD_P), b2_dash_share_list[i]))
        b3_inverse_share_list.append(
            mult(pow(B_list[i], -1, MOD_P), b3_dash_share_list[i]))

    # 6
    # c1_share_list = []
    # c2_share_list = []
    # c3_share_list = []
    c_list = []
    for i in range(0, BIT):
        if i == 0:
            share_1, share_2, share_3 = share_mult(
                A1_share, b1_inverse_share_list[i],
                A2_share, b2_inverse_share_list[i],
                A3_share, b3_inverse_share_list[i]
            )
            c_list.append(restore(share_1, share_2, share_3))
        else:
            share_1, share_2, share_3 = share_mult(
                A1_share, b1_inverse_share_list[i],
                A2_share, b2_inverse_share_list[i],
                A3_share, b3_inverse_share_list[i]
            )
            share_1, share_2, share_3 = share_mult(
                share_1, b1_share_list[i-1],
                share_2, b2_share_list[i-1],
                share_3, b3_share_list[i-1]
            )
            c_list.append(restore(share_1, share_2, share_3))

    A1_exp_list = []
    A2_exp_list = []
    A3_exp_list = []
    t = 1
    for i in range(0, BIT):
        t = mult(t, c_list[i])
        A1_exp_list.append(mult(t, b1_share_list[i]))
        A2_exp_list.append(mult(t, b2_share_list[i]))
        A3_exp_list.append(mult(t, b3_share_list[i]))

    # ラグランジュの未定係数法
    and_list = [
        1,
        1095567251290110014,
        15603599130927532848,
        3927973679664754768,
        13253920145236317331,
        5072689204291235733,
        3435840349470671764,
        16549778763406408630,
        12459576446030141042,
        10696557716079594807,
        3197018912709867365,
        9970630734852788482,
        10106868463622397398,
        6870526778099185113,
        16162773849234898198,
        6512084038109877353,
        17791231165580233294,
        4939553442392971102,
        6613779837673282520,
        6112835044719072700,
        11561852329015516476,
        3241087653075867336,
        11115359391888299599,
        1734929295488186025,
        11958404333307668373,
        1438215050425705879,
        11073690707525551423,
        17532628264929026480,
        6082710703763137390,
        5125529121156609847,
        3536240549677738615,
        168123567554747533,
        17222647251913610444,
        6314115150414057577,
        5720266728093558989,
        11315745394801430483,
        13585209705064903598,
        10609659846084906928,
        6341781282790677798,
        394864220565298862,
        5249871464994426133,
        13296832158245447365,
        12801767259528789327,
        8166545265620715462,
        12622067858020089155,
        10852787575795086238,
        15358952924301378654,
        14141418894305759068,
        13215619082908852856,
        9900973216959770499,
        11398882017370494561,
        1875791515713213273,
        18179510337970552075,
        12349041994205078879,
        4559441349647564738,
        4543633939816633313,
        9247229033112764012,
        9230709934058803069,
        12860062884571458050,
        14898881793951465380,
        9282848170176021024,
        16257860633325038337,
        546853837372292893,
        3893473855680099452,
        672143786416464336
    ]

    share_f1, share_f2, share_f3 = 0, 0, 0
    for index, value in enumerate(and_list):
        if index == 0:
            share_f1 = add(share_f1, value)
        else:
            share_f1 = add(share_f1, mult(value, A1_exp_list[index-1]))
            share_f2 = add(share_f2, mult(value, A2_exp_list[index-1]))
            share_f3 = add(share_f3, mult(value, A3_exp_list[index-1]))

    return share_f1, share_f2, share_f3


def sub_prefix_or(bit_share_list1, bit_share_list2, bit_share_list3): # test: ok
    # 1: check
    x1_share_list = []
    x2_share_list = []
    x3_share_list = []
    for i in range(0, LAMBDA):
        start = i
        end = i + LAMBDA
        x1, x2, x3 = sub_unbounded_fan_in_or(bit_share_list1[start:end]+[0]*(BIT-LAMBDA), bit_share_list2[start:end]+[0]*(BIT-LAMBDA), bit_share_list3[start:end]+[0]*(BIT-LAMBDA))
        x1_share_list.append(x1)
        x2_share_list.append(x2)
        x3_share_list.append(x3)
    
    # 2
    y1_share_list = []
    y2_share_list = []
    y3_share_list = []
    for i in range(0, LAMBDA):
        y1, y2, y3 = sub_unbounded_fan_in_or(x1_share_list[0:i+1]+[0]*(BIT-(i+1)), x2_share_list[0:i+1]+[0]*(BIT-(i+1)), x3_share_list[0:i+1]+[0]*(BIT-(i+1)))
        y1_share_list.append(y1)
        y2_share_list.append(y2)
        y3_share_list.append(y3)
    
    # 3
    f1_share_list = []
    f2_share_list = []
    f3_share_list = []
    for i in range(0, LAMBDA):
        if i == 0:
            f1_share_list.append(x1_share_list[i])
            f2_share_list.append(x2_share_list[i])
            f3_share_list.append(x3_share_list[i])
        else:
            f1_share_list.append(sub(y1_share_list[i], y1_share_list[i-1]))
            f2_share_list.append(sub(y2_share_list[i], y2_share_list[i-1]))
            f3_share_list.append(sub(y3_share_list[i], y3_share_list[i-1]))
    # 4
    a1_share_list = []
    a2_share_list = []
    a3_share_list = []
    for j in range(0, LAMBDA):
        a1_share_sum, a2_share_sum, a3_share_sum = 0, 0, 0
        for i in range(0, LAMBDA):
            index = LAMBDA*i+j
            a1, a2, a3 = share_mult(
                f1_share_list[i], bit_share_list1[index],
                f2_share_list[i], bit_share_list2[index],
                f3_share_list[i], bit_share_list3[index]
            )
            a1_share_sum = add(a1_share_sum, a1)
            a2_share_sum = add(a2_share_sum, a2)
            a3_share_sum = add(a3_share_sum, a3)
        a1_share_list.append(a1_share_sum)
        a2_share_list.append(a2_share_sum)
        a3_share_list.append(a3_share_sum)

    # 5
    b1_share_list = []
    b2_share_list = []
    b3_share_list = []
    for j in range(0, LAMBDA):
        b1, b2, b3 = sub_unbounded_fan_in_or(a1_share_list[0:j+1]+[0]*(BIT-j-1), a2_share_list[0:j+1]+[0]*(BIT-j-1), a3_share_list[0:j+1]+[0]*(BIT-j-1))
        b1_share_list.append(b1)
        b2_share_list.append(b2)
        b3_share_list.append(b3)

    # 6
    s1_share_list = []
    s2_share_list = []
    s3_share_list = []
    for i in range(0, BIT):
        if i < LAMBDA:
            s1_share_list.append(sub(y1_share_list[i], f1_share_list[i]))
            s2_share_list.append(sub(y2_share_list[i], f2_share_list[i]))
            s3_share_list.append(sub(y3_share_list[i], f3_share_list[i]))
        else:
            s1_share_list.append(1)
            s2_share_list.append(0)
            s3_share_list.append(0)
    
    # 7
    ret1_share_list = []
    ret2_share_list = []
    ret3_share_list = []
    for i in range(0, LAMBDA):
        for j in range(0, LAMBDA):
            index = LAMBDA*i + j
            r1, r2, r3 = share_mult(
                f1_share_list[i], b1_share_list[j],
                f2_share_list[i], b2_share_list[j],
                f3_share_list[i], b3_share_list[j]
            )
            r1 = add(r1, s1_share_list[i])
            r2 = add(r2, s2_share_list[i])
            r3 = add(r3, s3_share_list[i])
            ret1_share_list.append(r1)
            ret2_share_list.append(r2)
            ret3_share_list.append(r3)
    
    return ret1_share_list, ret2_share_list, ret3_share_list


def sub_bitwise_less_than(a1_bit_share_list, b1_bit_share_list, a2_bit_share_list, b2_bit_share_list, a3_bit_share_list, b3_bit_share_list):
    c1_share_list = []
    c2_share_list = []
    c3_share_list = []
    for i in range(0, BIT):
        t1 = add(a1_bit_share_list[i], b1_bit_share_list[i])
        t2 = add(a2_bit_share_list[i], b2_bit_share_list[i])
        t3 = add(a3_bit_share_list[i], b3_bit_share_list[i])
        s1, s2, s3 = share_mult(
            a1_bit_share_list[i], b1_bit_share_list[i],
            a2_bit_share_list[i], b2_bit_share_list[i],
            a3_bit_share_list[i], b3_bit_share_list[i]
        )
        s1 = mult(s1, 2)
        s2 = mult(s2, 2)
        s3 = mult(s3, 2)
        c1_share_list.append(sub(t1, s1))
        c2_share_list.append(sub(t2, s2))
        c3_share_list.append(sub(t3, s3))
    
    d1_share_list, d2_share_list, d3_share_list = [], [], []
    for i in range(0, BIT):
        index = BIT-i
        d1, d2, d3 = sub_unbounded_fan_in_or(c1_share_list[0:index], c2_share_list[0:index], c3_share_list[0:index])
        d1_share_list = [d1] + d1_share_list
        d2_share_list = [d2] + d2_share_list
        d3_share_list = [d3] + d3_share_list

    e1_share_list = []
    e2_share_list = []
    e3_share_list = []
    for i in range(0, BIT):
        if i == 0:
            e1_share_list.append(d1_share_list[i])
            e2_share_list.append(d2_share_list[i])
            e3_share_list.append(d3_share_list[i])
        else:
            e1_share_list.append(sub(d1_share_list[i], d1_share_list[i-1]))
            e2_share_list.append(sub(d2_share_list[i], d2_share_list[i-1]))
            e3_share_list.append(sub(d3_share_list[i], d3_share_list[i-1]))
    
    ret1, ret2, ret3 = 0, 0, 0
    for i in range(0, BIT):
        t1, t2, t3 = share_mult(
            e1_share_list[i], b1_bit_share_list[i],
            e2_share_list[i], b2_bit_share_list[i],
            e3_share_list[i], b3_bit_share_list[i]
        )
        ret1 = add(ret1, t1)
        ret2 = add(ret2, t2)
        ret3 = add(ret3, t3)
    return ret1, ret2, ret3


def sub_half_less_than_test(a1_share, a2_share, a3_share):
    r1_share_list, r2_share_list, r3_share_list = sub_rbvs()
    r1_share = decomposition(r1_share_list)
    r2_share = decomposition(r2_share_list)
    r3_share = decomposition(r3_share_list)

    c1_share = add(mult(2, a1_share), r1_share)
    c2_share = add(mult(2, a2_share), r2_share)
    c3_share = add(mult(2, a3_share), r3_share)
    c = restore(c1_share, c2_share, c3_share)
    c1_bit_share, c2_bit_share, c3_bit_share = composition(c)
    t1_share, t2_share, t3_share = sub_bitwise_less_than(c1_bit_share, r1_share_list, c2_bit_share, r2_share_list, c3_bit_share, r3_share_list)
    if c % 2 == 0:
        a1_share1, a2_share1, a3_share1 = share_mult(
            t1_share, sub(1, r1_share_list[BIT-1]),
            t2_share, sub(0, r2_share_list[BIT-1]),
            t3_share, sub(0, r3_share_list[BIT-1])
        )
        a1_share2, a2_share2, a3_share2 = share_mult(
            sub(1, t1_share), r1_share_list[BIT-1],
            sub(0, t2_share), r2_share_list[BIT-1],
            sub(0, t3_share), r3_share_list[BIT-1]
        )
    else:
        a1_share1, a2_share1, a3_share1 = share_mult(
            t1_share, r1_share_list[BIT-1],
            t2_share, r2_share_list[BIT-1],
            t3_share, r3_share_list[BIT-1]
        )
        a1_share2, a2_share2, a3_share2 = share_mult(
            sub(1, t1_share), sub(1, r1_share_list[BIT-1]),
            sub(0, t2_share), sub(0, r2_share_list[BIT-1]),
            sub(0, t3_share), sub(0, r3_share_list[BIT-1])
        )
    
    return sub(1, add(a1_share1, a1_share2)), sub(0, add(a2_share1, a2_share2)), sub(0, add(a3_share1, a3_share2))



def decomposition(r_share_list):
    l = len(r_share_list)
    ans = 0
    for i in range(0, l):
        ans = add(ans, mult(2**(l-1-i), r_share_list[i]))
    return ans


def composition(c):
    c_list = [int(x) for x in bin(c)[2:]]
    c_list = [0]*(BIT-len(c_list)) + c_list
    r1, r2, _ = sub_rbvs()
    r3 = []
    for i in range(0, BIT):
        r3.append(sub(c_list[i], add(r1[i], r2[i])))
    return r1, r2, r3

def f_or(x):
    ans = 0
    for j in range(2, BIT+2):
        ans += lagrange(j, x)
    return ans


def f_and(x):
    return lagrange(BIT+1, x)


def lagrange(j: int, x: int):
    ans = 1
    for i in range(1, BIT+2):
        if j != i:
            ans = mult(ans, sub(x, i))
            ans = mult(ans, pow(sub(j, i), -1, MOD_P))
    return ans


def restore(x1, x2, x3):  # test: ok
    t1 = add(x1, x2)
    t2 = add(t1, x3)
    return t2


# =======================
# main protocols
# =======================
def interval_test(c1, c2, a1_share, a2_share, a3_share):
    r1_share_list, r2_share_list, r3_share_list = sub_rbvs()
    r1_share = decomposition(r1_share_list)
    r2_share = decomposition(r2_share_list)
    r3_share = decomposition(r3_share_list)
    c1_share = add(a1_share, r1_share)
    c2_share = add(a2_share, r2_share)
    c3_share = add(a3_share, r3_share)
    c = restore(c1_share, c2_share, c3_share)
    if not ((c1 < c) and (c < c2)):
        if c2 <= c:
            r_row = c - c2
            r_high = c - c1
        elif (c <= c1):
            r_row = c + MOD_P - c2
            r_high = c + MOD_P - c1
        r1_row, r2_row, r3_row = composition(r_row)
        r1_high, r2_high, r3_high = composition(r_high)
        t1_row, t2_row, t3_row = sub_bitwise_less_than(r1_row, r1_share_list, r2_row, r2_share_list, r3_row, r3_share_list)
        t1_high, t2_high, t3_high = sub_bitwise_less_than(r1_share_list, r1_high, r2_share_list, r2_high, r3_share_list, r3_high)
        ret1, ret2, ret3 = share_mult(
            t1_row, t1_high,
            t2_row, t2_high,
            t3_row, t3_high
        )
        return ret1, ret2, ret3
    else:
        r_row = (c - c1 - 1) % MOD_P
        r_high = (c + MOD_P - c2 + 1) % MOD_P
        r1_row, r2_row, r3_row = composition(r_row)
        r1_high, r2_high, r3_high = composition(r_high)
        t1_row, t2_row, t3_row = sub_bitwise_less_than(
            r1_row, r1_share_list, r2_row, r2_share_list, r3_row, r3_share_list)
        t1_high, t2_high, t3_high = sub_bitwise_less_than(
            r1_share_list, r1_high, r2_share_list, r2_high, r3_share_list, r3_high)
        ret1, ret2, ret3 = share_mult(
            t1_row, t1_high,
            t2_row, t2_high,
            t3_row, t3_high
        )
        return sub(1, ret1), sub(0, ret2), sub(0, ret3)

def comparison_test(a1_share, b1_share, a2_share, b2_share, a3_share, b3_share):
    w1_share, w2_share, w3_share = sub_half_less_than_test(a1_share, a2_share, a3_share)
    x1_share, x2_share, x3_share = sub_half_less_than_test(b1_share, b2_share, b3_share)
    y1_share, y2_share, y3_share = sub_half_less_than_test(
        sub(a1_share, b1_share),
        sub(a2_share, b2_share),
        sub(a3_share, b3_share)
    )
    t1_share, t2_share, t3_share = share_mult(
        x1_share, y1_share,
        x2_share, y2_share,
        x3_share, y3_share
    )
    xy1_share, xy2_share, xy3_share = t1_share, t2_share, t3_share
    t1_share = mult(2, t1_share)
    t1_share = sub(add(x1_share, y1_share), t1_share)
    t2_share = mult(2, t2_share)
    t2_share = sub(add(x2_share, y2_share), t2_share)
    t3_share = mult(2, t3_share)
    t3_share = sub(add(x3_share, y3_share), t3_share)

    t1_share, t2_share, t3_share = share_mult(
        w1_share, t1_share,
        w2_share, t2_share,
        w3_share, t3_share
    )
    t1_share = add(t1_share, 1)
    t1_share = sub(t1_share, y1_share)
    t1_share = sub(t1_share, x1_share)
    t1_share = add(t1_share, xy1_share)

    t2_share = add(t2_share, 0)
    t2_share = sub(t2_share, y2_share)
    t2_share = sub(t2_share, x2_share)
    t2_share = add(t2_share, xy2_share)

    t3_share = add(t3_share, 0)
    t3_share = sub(t3_share, y3_share)
    t3_share = sub(t3_share, x3_share)
    t3_share = add(t3_share, xy3_share)

    return t1_share, t2_share, t3_share

def equality_test(a1_share, b1_share, a2_share, b2_share, a3_share, b3_share):
    r1_share_list, r2_share_list, r3_share_list = sub_rbvs()
    r1_share = decomposition(r1_share_list)
    r2_share = decomposition(r2_share_list)
    r3_share = decomposition(r3_share_list)
    c1_share = add(sub(a1_share, b1_share), r1_share)
    c2_share = add(sub(a2_share, b2_share), r2_share)
    c3_share = add(sub(a3_share, b3_share), r3_share)
    c = restore(c1_share, c2_share, c3_share)
    c_list = [int(x) for x in bin(c)[2:]]
    c_list = [0]*(BIT-len(c_list)) + c_list
    c1_dash_list = []
    c2_dash_list = []
    c3_dash_list = []
    for i in range(0, BIT):
        if c_list[i] == 1:
            c1_dash_list.append(r1_share_list[i])
            c2_dash_list.append(r2_share_list[i])
            c3_dash_list.append(r3_share_list[i])
        else:
            c1_dash_list.append(sub(1, r1_share_list[i]))
            c2_dash_list.append(sub(0, r2_share_list[i]))
            c3_dash_list.append(sub(0, r3_share_list[i]))
    
    ret1, ret2, ret3 = sub_unbounded_fan_in_and(c1_dash_list, c2_dash_list, c3_dash_list)
    return ret1, ret2, ret3



# =======================
# main function
# =======================
if __name__ == '__main__':
    # RBS
    # share1, share2, share3 = sub_rbs()
    # print('RBS: ', restore(share1, share2, share3))

    # RBVS
    # shares1, shares2, shares3 = sub_rbvs()
    share1, share2, share3 = sub_rns()
    share11, share22, share33 = sub_rns()
    ret1, ret2, ret3 = equality_test(share1, share11, share2, share22, share3, share33)
    print((ret1 + ret2 + ret3) % MOD_P)
