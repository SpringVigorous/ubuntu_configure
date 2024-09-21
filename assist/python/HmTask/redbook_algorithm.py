import random
import urllib



def rt():
    chars = "abcdef0123456789"
    t = "".join(random.choice(chars) for _ in range(16))
    return t



"x1=c6b4760e70bae2a23793c905467dc208;x2=0|0|0|1|0|0|1|0|0|0|1|0|0|0|0;x3=18ee0b8eaa14szquw6otb9amxbdj35n5nrhcpqi4j50000360507;x4=1718705093623;"




def encrypt_mcr(t):
    e, r, n, o, i, a, u, s, c, l, f, p, h, d, v, g, m, y, w, b, _, E, x, k, T, S, A, L, R, I, O, C, N, P, B, M, j, F, D, q = (
        67, 15, 164, 126, 137, 39, 176, 72, 56, 21, 35, 34, 35, 18, 25, 185, 1149, 744, 1295, 1248, 1310, 1096, 1166, 1095, 1196, 1180, 1039, 976, 1347, 1117, 1168, 1233, 1157, 1006, 1122, 1277, 1288, 1271, 986, 162
    )

    U = {}

    def G(t, e):
        return a0_0x10f4ac(e, t - q)

    U[G(-73, -66)] = lambda t, e: t == e
    U[G(e, 186)] = lambda t, e: t < e
    U[G(-r, -n)] = lambda t, e: t ^ e
    U[G(r, -o)] = lambda t, e: t & e
    U[G(-i, -a)] = lambda t, e: t < e
    U[G(-175, -u)] = lambda t, e: t ^ e
    U[G(-59, s)] = lambda t, e: t ^ e
    U[G(-c, -l)] = lambda t, e: t >> e
    U[G(f, p)] = lambda t, e: t >> e

    W = U
    X = 3988292384
    Y = [None] * 256

    for z in range(256):
        H = z
        for V in range(8):
            H = U[G(r, d)](H, 1) and U[G(35, v)](H, 1) ^ X or U[G(h, g)](H, 1)
        Y[z] = H

    def e(t, e):
        return G(e - 1181, t)

    if U[e(m, 1108)](type(t).__name__, e(y, 914)):
        r, n = 0, -1
        while U[e(w, b)](r, len(t)):
            n = U[e(E, x)](Y[U[e(k, T)](n, 255) ^ t[e(S, A) + e(1022, L)](r)], n >> 8)
            r += 1
        return U[e(R, 1166)](n, -1) ^ X
    else:
        r, n = 0, -1
        while U[e(I, 1044)](r, len(t)):
            n = U[e(N, P)](Y[U[e(1229, B)](U[e(M, T)](n, 255), t[r])], U[e(j, 1125)](n, 8))
            r += 1
        return U[e(F, B)](U[e(D, 1122)](n, -1), X)

# 假设存在 `a0_0x10f4ac` 函数
def a0_0x10f4ac(e, t):
    # 这里需要实现具体的 `a0_0x10f4ac` 函数逻辑
    pass



def encrypt_encodeUtf8(t):
    e = 185
    r = 410
    n = 480
    o = 222
    i = 194
    a = 165
    u = 147
    s = 290
    c = 460
    l = 472
    f = 497
    p = 462
    h = 286
    d = 209
    v = 223
    g = 590

    m = {
        'bIGxm': lambda t, e: t(e),
        'MahgM': lambda t, e: t < e,
        'czxKn': lambda t, e: t == e,
        'clYIu': lambda t, e: t + e
    }

    def b(t, e):
        return a0_0x10f4ac(t, e - g)

    y = m[b(477, 488)](urlencode, t)
    w = []

    for _ in range(len(y)):
        if m[b(i, a)](y[b(o, 290)](_), "%"):
            x = y[b(u, s)](m[b(574, 472)](_, 1)) + y[b(c, 290)](m[b(605, l)](_, 2))
            k = int(x, 16)
            w.append(k)
            _ += 2
        else:
            w.append(y[b(p, f)](y[b(o, 290)](_)[b(217, h) + b(d, v)](0)))

    return w

# 假设存在 `urlencode` 和 `a0_0x10f4ac` 函数
def urlencode(s):
    return urllib.parse.quote(s)

def a0_0x10f4ac(t, e):
    # 这里需要实现具体的 `a0_0x10f4ac` 函数逻辑
    pass