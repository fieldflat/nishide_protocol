import math
import random

# ===========
# Constants
# ===========
BIT = 32
MOD_P = 2**BIT - 5
MAX_INTEGER = 2**(2*BIT) - 1
BEAVERS_TRIPLE = [[1, 2, 4], [2, 5, 1], [13, 29, 14]]

# =====================================================================
# PrimeField is the class which is used to execute comparison protocol.
# =====================================================================


class PrimeField:
    def __init__(self, value: int):
        self.value: int = value

    def is_validate_value(self):
        if (0 <= self.value) and (self.value < MOD_P):
            return True
        print("[Error] invalidate value")
        exit(1)

    def is_overflow(self):
        if (0 <= self.value) and (self.value < MAX_INTEGER + 1):
            return False
        print("[Error] overflow happens.")
        exit(1)

    def reduction(self):
        if not self.is_overflow():
            self.value = self.value % MOD_P

    def add(self, n):
        if self.is_validate_value() and n.is_validate_value():
            self.value += n.value
            if not self.is_overflow():
                self.reduction()

    def sub(self, n):
        if self.is_validate_value() and n.is_validate_value():
            if self.value < n.value:
                self.value += MOD_P
                if not self.is_overflow():
                    self.value -= n.value
                    self.reduction()
            else:
                self.value -= n.value
                self.reduction()

    def multiply(self, n):
        if self.is_validate_value() and n.is_validate_value():
            self.value *= n.value
            if not self.is_overflow():
                self.reduction()

    def inv(self):
        if self.is_validate_value():
            self.value = pow(self.value, -1, MOD_P)  # inverse

# =============
# Party class
# =============


class Party:
    def __init__(self, name):
        self.name: str = name
        self.share_r: PrimeField = PrimeField(value=-1)
        self.share_d: PrimeField = PrimeField(value=-1)
        self.share_e: PrimeField = PrimeField(value=-1)
        self.share_z: PrimeField = PrimeField(value=-1)

    def generate_beavers_share(self, x: PrimeField, y: PrimeField):
        # 7*8 = 56 (a = 7, b = 8, c = 56)
        if self.name == "P1":
            (share_a, share_b, share_c) = (
                BEAVERS_TRIPLE[0][0], BEAVERS_TRIPLE[1][0], BEAVERS_TRIPLE[2][0])
        elif self.name == "P2":
            (share_a, share_b, share_c) = (
                BEAVERS_TRIPLE[0][1], BEAVERS_TRIPLE[1][1], BEAVERS_TRIPLE[2][1])
        elif self.name == "P3":
            (share_a, share_b, share_c) = (
                BEAVERS_TRIPLE[0][2], BEAVERS_TRIPLE[1][2], BEAVERS_TRIPLE[2][2])
        else:
            print("[Error] invalid party.")
            exit(1)
        self.share_d = PrimeField(value=x.value - share_a)
        self.share_e = PrimeField(value=y.value - share_b)

    def sub_rns(self):
        r = random.randint(1, MOD_P)
        self.share_r = PrimeField(value=r)
        print("{0} generates share_r = {1}".format(
            self.name, self.share_r.value))


# ==========================
def is_overflow(value):
    if (0 <= value) and (value < MAX_INTEGER + 1):
        return False
    print("[Error] overflow happens.")
    exit(1)


def restore(PF1: PrimeField, PF2: PrimeField, PF3: PrimeField) -> PrimeField:
    print("restore: ({0}, {1}, {2})".format(PF1.value, PF2.value, PF3.value))
    r = PF1.value + PF2.value + PF3.value
    if not is_overflow(r):
        return PrimeField(value=r % MOD_P)


#
#
# Protocol
#
#
def legendre(a, p):
    return pow(a, (p - 1) // 2, p)


def tonelli_shanks(a, p):
    if legendre(a, p) != 1:
        raise Exception("not a square (mod p)")
    # Step 1. By factoring out powers of 2, find q and s such that p - 1 = q 2^s with Q odd
    q = p - 1
    s = 0
    while q % 2 == 0:
        q >>= 1
        s += 1
    # Step 2. Search for a z in Z/pZ which is a quadratic non-residue
    for z in range(2, p):
        if legendre(z, p) == p - 1:
            break
    # Step 3.
    m = s
    c = pow(z, q, p)  # quadratic non residue
    t = pow(a, q, p)  # quadratic residue
    r = pow(a, (q + 1) // 2, p)
    # Step 4.
    t2 = 0
    while True:
        if t == 0:
            return 0
        if t == 1:
            return r
        t2 = (t * t) % p
        for i in range(1, m):
            if t2 % p == 1:
                break
            t2 = (t2 * t2) % p
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p


def sub_rns(P1: Party, P2: Party, P3: Party) -> PrimeField:
    P1.sub_rns()
    P2.sub_rns()
    P3.sub_rns()
    r = restore(P1.share_r, P2.share_r, P3.share_r)
    print("sub_rns generates {0}".format(r.value))
    return r


def sub_rbs(P1: Party, P2: Party, P3: Party) -> PrimeField:
    P1.sub_rns()
    P2.sub_rns()
    P3.sub_rns()
    P1.generate_beavers_share(x=PrimeField(value=4), y=PrimeField(value=5))
    P2.generate_beavers_share(x=PrimeField(value=2), y=PrimeField(value=1))
    P3.generate_beavers_share(x=PrimeField(value=5), y=PrimeField(value=2))
    d = restore(P1.share_d, P2.share_d, P3.share_d)
    e = restore(P1.share_e, P2.share_e, P3.share_e)
    P1.share_z.value = e.value*BEAVERS_TRIPLE[0][0] + d.value * \
        BEAVERS_TRIPLE[1][0] + BEAVERS_TRIPLE[2][0] + d.value*e.value
    P1.share_z.reduction()
    P2.share_z.value = e.value*BEAVERS_TRIPLE[0][1] + d.value * \
        BEAVERS_TRIPLE[1][1] + BEAVERS_TRIPLE[2][1] + d.value*e.value
    P2.share_z.reduction()
    P3.share_z.value = e.value*BEAVERS_TRIPLE[0][2] + d.value * \
        BEAVERS_TRIPLE[1][2] + BEAVERS_TRIPLE[2][2] + d.value*e.value
    P3.share_z.reduction()
    r2 = restore(P1.share_z, P2.share_z, P3.share_z)
    r = restore(P1.share_r, P2.share_r, P3.share_r)
    print("sub_rbs generates {0}".format(r2.value))
    if r2.value == 0:
        print("[Error] r2 is 0.")
        exit(1)
    # r_dash = tonelli_shanks(r2.value, MOD_P)
    r_dash = min(r.value, MOD_P-r.value)
    r_dash_inverse = pow(r_dash, -1, MOD_P)
    a1_share = PrimeField(value=r_dash_inverse * P1.share_r.value + 1)
    a1_share.reduction()
    a2_share = PrimeField(value=r_dash_inverse * P2.share_r.value + 0)
    a2_share.reduction()
    a3_share = PrimeField(value=r_dash_inverse * P3.share_r.value + 0)
    a3_share.reduction()
    r = restore(a1_share, a2_share, a3_share)
    print("sub_rns generates {0}".format(r.value // 2))
    return r


if __name__ == '__main__':
    P1 = Party("P1")
    P2 = Party("P2")
    P3 = Party("P3")
    sub_rns(P1, P2, P3)
    sub_rbs(P1, P2, P3)
