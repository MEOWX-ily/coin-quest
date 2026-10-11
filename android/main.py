#!/usr/bin/env python3
"""ILYSHOOT - tactical platformer (pygame).   Run:  python main.py"""
import array, math, os, random, types
import pygame as pg

T, W, H = 40, 960, 520
NS = types.SimpleNamespace
AMB, RED, INK, DIM = (255, 159, 28), (224, 57, 45), (216, 220, 207), (138, 146, 125)

# pl = platforms (col,row,len)  sp = spikes  co = coin rows (col,row,count)
# en = enemies (col,row,patrol_from_col,patrol_to_col)  pit = ground gaps
LV = [
 dict(n='Dustline', w=64, fl=60, pit=[(18, 19), (38, 40)],
  pl=[(10, 8, 4), (22, 8, 3), (26, 6, 3), (30, 8, 4), (44, 8, 3), (48, 6, 4), (53, 8, 3)],
  sp=[(27, 10), (28, 10), (35, 10), (36, 10), (51, 10), (52, 10)],
  co=[(10, 7, 4), (18, 9, 2), (22, 7, 3), (26, 5, 3), (30, 7, 4), (39, 9, 3), (44, 7, 3), (48, 5, 4), (53, 7, 3)],
  en=[(8, 10, 5, 13), (23, 10, 20, 25), (31, 10, 29, 33), (45, 10, 42, 49)]),
 dict(n='Iron Bridge', w=80, fl=77, pit=[(12, 14), (28, 31), (46, 48), (62, 65)],
  pl=[(16, 8, 3), (20, 6, 3), (24, 8, 3), (29, 8, 2), (33, 8, 3), (37, 6, 3), (41, 8, 3), (50, 8, 3), (54, 6, 4), (59, 8, 2), (63, 8, 2), (68, 8, 3), (72, 6, 3)],
  sp=[(17, 10), (18, 10), (34, 10), (35, 10), (36, 10), (52, 10), (53, 10), (69, 10), (70, 10)],
  co=[(12, 9, 3), (16, 7, 3), (20, 5, 3), (24, 7, 3), (33, 7, 3), (37, 5, 3), (41, 7, 3), (54, 4, 4), (63, 7, 2), (68, 7, 3), (72, 5, 3)],
  en=[(8, 10, 5, 11), (23, 10, 20, 26), (41, 10, 38, 44), (57, 10, 55, 60), (73, 10, 71, 75), (55, 5, 54, 57)]),
 dict(n='Blackout', w=96, fl=93, pit=[(10, 12), (22, 25), (34, 37), (50, 53), (66, 70), (80, 82)],
  pl=[(10, 8, 3), (15, 8, 2), (19, 5, 3), (23, 8, 2), (28, 8, 3), (32, 6, 2), (35, 8, 2), (40, 8, 3), (44, 6, 3), (48, 8, 2), (51, 8, 2), (55, 8, 3), (60, 6, 3), (67, 8, 2), (72, 8, 3), (76, 6, 3), (81, 8, 2), (86, 8, 3), (90, 6, 3)],
  sp=[(14, 10), (15, 10), (16, 10), (29, 10), (30, 10), (41, 10), (42, 10), (43, 10), (56, 10), (57, 10), (58, 10), (74, 10), (75, 10), (76, 10), (88, 10)],
  co=[(10, 7, 3), (19, 4, 3), (23, 7, 2), (28, 6, 3), (32, 5, 2), (44, 4, 3), (60, 4, 3), (67, 7, 2), (76, 4, 3), (86, 7, 3), (90, 5, 3)],
  en=[(6, 10, 4, 9), (19, 10, 17, 21), (29, 7, 28, 30), (46, 10, 44, 49), (45, 5, 44, 46), (62, 10, 59, 65), (61, 5, 60, 62), (77, 5, 76, 78), (85, 10, 83, 87)]),
]

# name: (start_hz, seconds, wave, volume, end_hz)
SFX = dict(jump=(380, .14, 'sq', .12, 760), coin=(880, .09, 'sq', .10, 1320), stomp=(220, .15, 'saw', .14, 60),
           shoot=(700, .08, 'saw', .10, 150), eshoot=(260, .10, 'sq', .08, 90), hurt=(150, .25, 'saw', .16, 60),
           reload=(300, .08, 'sq', .08, 500), win=(523, .5, 'tri', .15, 1046), fail=(110, .6, 'saw', .18, 40),
           pit=(120, .3, 'saw', .16, 50))


def tone(f, d, wave, vol, f2):
    try:
        n = int(22050 * d); a = array.array('h'); ph = 0.0
        for i in range(n):
            ph += (f + (f2 - f) * i / n) / 22050
            p = ph % 1
            v = (1 if p < .5 else -1) if wave == 'sq' else (2 * p - 1) if wave == 'saw' else 4 * abs(p - .5) - 1
            a.append(int(v * vol * 32767 * (1 - i / n)))
        return pg.mixer.Sound(buffer=a.tobytes())
    except Exception:
        return None


def hit(a, b):
    return a.x < b.x + b.w and a.x + a.w > b.x and a.y < b.y + b.h and a.y + a.h > b.y


class Game:
    def __init__(s):
        pg.mixer.pre_init(22050, -16, 1, 512, allowedchanges=0)
        pg.init()
        s.android = 'ANDROID_ARGUMENT' in os.environ
        try:
            flags = pg.SCALED | pg.FULLSCREEN if s.android else pg.SCALED | pg.RESIZABLE
            s.scr = pg.display.set_mode((W, H), flags)
        except Exception:
            s.scr = pg.display.set_mode((W, H), pg.FULLSCREEN if s.android else 0)
        s.android = s.android or pg.display.get_driver() == 'android'
        pg.display.set_caption('ILYSHOOT')
        mk = lambda n: pg.font.SysFont('impact,arialblack,arial', n)
        s.fb, s.fm, s.fs = mk(64), mk(26), mk(20)
        s.snd = {k: tone(*v) for k, v in SFX.items()}
        s.surf = pg.Surface((W, H)).convert()
        s.art()
        s.st, s.cur, s.sc0, s.feed, s.shk, s.an, s.jp = 'menu', 0, {0: 0}, [], 0, 0, False
        s.fingers, s.touch_jump_prev = {}, False
        s.load(0)
        s.ov = dict(title='ILYSHOOT', btn='DEPLOY', lines=[
            'OPERATION GOLD RUSH', 'ARROWS / A D MOVE    SPACE / W JUMP    F OR CLICK FIRE',
            'STOMP OR SHOOT HOSTILES. THE 2 NEAREST SHOOT BACK.', 'AVOID SPIKES. REACH EXTRACTION.'])
        s.act = lambda: s.start(0)

    # ---------- level ----------
    def load(s, i):
        s.lv = lv = LV[i]; w = lv['w']
        s.g = [[0] * w for _ in range(13)]
        for c in range(w):
            if not any(a <= c <= b for a, b in lv['pit']):
                s.g[11][c] = s.g[12][c] = 1
        for c0, r, n in lv['pl']:
            for k in range(n): s.g[r][c0 + k] = 1
        for c, r in lv['sp']: s.g[r][c] = 2
        s.C = [NS(x=(c0 + k) * T + 20, y=r * T + 20, got=0) for c0, r, n in lv['co'] for k in range(n)]
        s.E = [NS(x=a * T, y=(r + 1) * T - 30, w=30, h=30, a=a * T, b=(b + 1) * T - 30, v=1 + i * .3, dead=0, f=0, t=0)
               for _, r, a, b in lv['en']]
        s.P = NS(x=80, y=406, w=22, h=34, vx=0, vy=0, face=1, gr=0, co=0, jb=0, jm=0)
        s.ck = (80, 406)
        s.coins = s.kills = s.t = s.cam = s.cd = s.rel = 0
        s.hp, s.inv, s.ammo = 3, 60, 6
        s.parts, s.bul, s.eb = [], [], []
        s.score = s.sc0.get(i, 0)

    def tile(s, c, r):
        if c < 0 or c >= s.lv['w']: return 1
        return s.g[r][c] if 0 <= r <= 12 else 0

    def sol(s, o):
        for r in range(int(o.y // T), int((o.y + o.h - .01) // T) + 1):
            for c in range(int(o.x // T), int((o.x + o.w - .01) // T) + 1):
                if s.tile(c, r) == 1: return 1
        return 0

    def sfx(s, k):
        q = s.snd.get(k)
        if q: q.play()

    def kf(s, text): s.feed.insert(0, [text, 110])

    def boom(s, x, y, c, n=12):
        for _ in range(n):
            s.parts.append(NS(x=x, y=y, vx=(random.random() - .5) * 6, vy=-random.random() * 5, l=30, c=c))

    def start(s, i):
        s.cur = i; s.load(i); s.st = 'play'; s.feed = []; s.kf('OBJECTIVE: REACH EXTRACTION')

    def hurt(s):
        if s.inv > 0 or s.st != 'play': return
        P = s.P; s.hp -= 1; s.inv = 90; P.vy = -7; P.vx = -P.face * 5; s.shk = 12
        s.kf('HIT TAKEN'); s.sfx('hurt')
        if s.hp <= 0: s.fail()

    def win(s):
        s.st = 'win'; sec = s.t / 60; bonus = max(0, round((90 - sec) * 3)); s.score += bonus
        s.sc0[s.cur + 1] = s.score; s.sfx('win')
        last = s.cur == len(LV) - 1; al = s.coins == len(s.C)
        rank = 'S' if al and s.hp == 3 else 'A' if al else 'B'
        s.ov = dict(title='OPERATION COMPLETE' if last else 'MISSION COMPLETE', btn='REDEPLOY' if last else 'NEXT MISSION', lines=[
            '%s // RANK %s' % (s.lv['n'].upper(), rank),
            'COINS %d/%d    KILLS %d    TIME %ds    BONUS +%d' % (s.coins, len(s.C), s.kills, sec, bonus),
            'TOTAL SCORE %d' % s.score])
        s.act = lambda: s.start(0 if last else s.cur + 1)

    def fail(s):
        s.st = 'fail'; s.sfx('fail')
        s.ov = dict(title='MISSION FAILED', col=RED, btn='RETRY', lines=['KIA // ' + s.lv['n'].upper()])
        s.act = lambda: s.start(s.cur)

    def fire(s):
        if s.st != 'play' or s.cd > 0 or s.rel > 0 or s.ammo <= 0: return
        P = s.P; s.ammo -= 1; s.cd = 12
        s.bul.append(NS(x=P.x + (34 if P.face > 0 else -12), y=P.y + 18, v=P.face * 13, l=0)); s.sfx('shoot')
        if s.ammo <= 0: s.rel = 75

    def inp(s):
        k, m = pg.key.get_pressed(), pg.mouse.get_pressed()
        left = s.android and s.touch(74, 452)
        right = s.android and s.touch(168, 452)
        jump = s.android and s.touch(730, 452)
        if jump and not s.touch_jump_prev: s.jp = True
        s.touch_jump_prev = jump
        return (k[pg.K_LEFT] or k[pg.K_a] or left, k[pg.K_RIGHT] or k[pg.K_d] or right,
                k[pg.K_SPACE] or k[pg.K_UP] or k[pg.K_w] or jump,
                k[pg.K_f] or k[pg.K_j] or k[pg.K_k] or (s.android and s.touch(870, 452)) or (m[0] and not s.android))

    def touch(s, x, y):
        return any((fx - x) ** 2 + (fy - y) ** 2 <= 54 ** 2 for fx, fy in s.fingers.values())

    # ---------- one 60 fps tick ----------
    def step(s):
        P = s.P; L, R, J, F = s.inp(); s.t += 1
        d = int(bool(R)) - int(bool(L))
        if d: P.face = d
        P.vx += (d * 4.4 - P.vx) * .22
        if s.jp: P.jb = 7; s.jp = False
        P.jb -= 1; P.co = 7 if P.gr else P.co - 1
        if P.jb > 0 and P.co > 0:
            P.vy = -12.5; P.jb = P.co = 0; P.jm = 1; s.sfx('jump')
        if not J and P.jm and P.vy < -5: P.vy = -5
        P.vy = min(P.vy + .55, 14)
        P.x += P.vx
        if s.sol(P):
            P.x = (P.x + P.w) // T * T - P.w if P.vx > 0 else P.x // T * T + T
            P.vx = 0
        P.gr = 0; P.y += P.vy
        if s.sol(P):
            if P.vy > 0: P.y = (P.y + P.h) // T * T - P.h; P.gr = 1; P.jm = 0
            else: P.y = P.y // T * T + T
            P.vy = 0
        if P.gr:
            r = int((P.y + P.h + 1) // T)
            if s.tile(int((P.x + 1) // T), r) == 1 and s.tile(int((P.x + P.w - 1) // T), r) == 1: s.ck = (P.x, P.y)
        s.inv -= 1
        for r in range(int(P.y // T), int((P.y + P.h - 1) // T) + 1):
            for c in range(int(P.x // T), int((P.x + P.w - 1) // T) + 1):
                if s.tile(c, r) == 2 and hit(P, NS(x=c * T + 6, y=r * T + 18, w=T - 12, h=T - 18)): s.hurt()
        if s.st != 'play': return
        if P.y > H + 40:
            s.hp -= 1
            if s.hp <= 0: return s.fail()
            P.x, P.y = s.ck; P.vx = P.vy = 0; s.inv = 90; s.sfx('pit')
        for e in s.E:
            if e.dead: continue
            e.x += e.v
            if e.x < e.a or e.x > e.b: e.v *= -1; e.x = max(e.a, min(e.b, e.x))
            if hit(P, e):
                if P.vy > 0 and P.y + P.h - P.vy <= e.y + 14:
                    e.dead = 1; P.vy = -12 if J else -8.5; P.jm = 0; s.kills += 1; s.score += 100
                    s.kf('+100 HOSTILE DOWN'); s.boom(e.x + 15, e.y + 15, (214, 58, 47)); s.sfx('stomp')
                else: s.hurt()
        if F: s.fire()
        if s.cd > 0: s.cd -= 1
        if s.rel > 0:
            s.rel -= 1
            if s.rel == 0: s.ammo = 6; s.sfx('reload')
        for b in s.bul:
            b.x += b.v; b.l += 1
            if s.tile(int(b.x // T), int(b.y // T)) == 1: b.l = 99
            for e in s.E:
                if not e.dead and b.l < 99 and e.x < b.x < e.x + e.w and e.y < b.y < e.y + e.h:
                    e.dead = 1; b.l = 99; s.kills += 1; s.score += 50
                    s.kf('+50 HOSTILE NEUTRALIZED'); s.boom(e.x + 15, e.y + 15, (214, 58, 47)); s.sfx('stomp')
        s.bul = [b for b in s.bul if b.l < 45]
        near = sorted((e for e in s.E if not e.dead), key=lambda e: math.hypot(e.x - P.x, e.y - P.y))[:2]
        ids = {id(e) for e in near}
        for e in s.E:
            e.f = 1 if e.v > 0 else -1
            if id(e) not in ids: e.t = 0
        for e in near:
            dx = P.x - e.x; e.f = 1 if dx > 0 else -1
            if abs(dx) < 520 and abs(P.y - e.y) < 150:
                e.t += 1
                if e.t > 120 - s.cur * 20:
                    e.t = 0; s.eb.append(NS(x=e.x + (32 if e.f > 0 else -2), y=e.y + 18, v=e.f * 5, l=0)); s.sfx('eshoot')
            else: e.t = 0
        for b in s.eb:
            b.x += b.v; b.l += 1
            if s.tile(int(b.x // T), int(b.y // T)) == 1: b.l = 999
            elif hit(P, NS(x=b.x - 4, y=b.y - 2, w=8, h=5)): b.l = 999; s.hurt()
        s.eb = [b for b in s.eb if b.l < 150]
        for o in s.C:
            if not o.got and math.hypot(o.x - P.x - 11, o.y - P.y - 17) < 24:
                o.got = 1; s.coins += 1; s.score += 10; s.boom(o.x, o.y, (255, 194, 60), 5); s.sfx('coin')
        if hit(P, NS(x=s.lv['fl'] * T + 6, y=2 * T, w=32, h=9 * T)): return s.win()
        for p in s.parts: p.x += p.vx; p.y += p.vy; p.vy += .3; p.l -= 1
        s.parts = [p for p in s.parts if p.l > 0]
        s.cam += (max(0, min(s.lv['w'] * T - W, P.x - W / 2 + 11 + P.face * 40)) - s.cam) * .1

    def event(s, e):
        if e.type == pg.KEYDOWN:
            k = e.key
            if k == pg.K_ESCAPE: pg.event.post(pg.event.Event(pg.QUIT))
            elif k == pg.K_F11: pg.display.toggle_fullscreen()
            elif s.st != 'play':
                if k in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE): s.act()
            elif k in (pg.K_SPACE, pg.K_UP, pg.K_w): s.jp = True
            elif k == pg.K_r: s.start(s.cur)
        elif e.type == pg.FINGERDOWN:
            s.fingers[e.finger_id] = (e.x * W, e.y * H)
            if s.st != 'play': s.act()
        elif e.type == pg.FINGERMOTION:
            s.fingers[e.finger_id] = (e.x * W, e.y * H)
        elif e.type == pg.FINGERUP:
            s.fingers.pop(e.finger_id, None)
        elif e.type == pg.MOUSEBUTTONDOWN and e.button == 1 and s.st != 'play': s.act()

    # ---------- art ----------
    def art(s):
        def blk(pf, up):
            u = pg.Surface((T, T)).convert(); u.fill((58, 66, 52) if pf else (37, 43, 32))
            pg.draw.rect(u, (74, 84, 66) if pf else (47, 54, 40), (2, 2, T - 4, T - 4))
            if not up: pg.draw.rect(u, (201, 138, 22) if pf else (109, 126, 58), (0, 0, T, 5))
            if pf:
                for xx in (5, T - 9): pg.draw.rect(u, (22, 27, 19), (xx, T - 10, 4, 4))
            return u
        s.tl = {(a, b): blk(a, b) for a in (0, 1) for b in (0, 1)}
        s.spk = pg.Surface((T, T), pg.SRCALPHA); pg.draw.rect(s.spk, (26, 31, 23), (0, T - 6, T, 6))
        for k in range(3):
            p = [(k * 13.3 + 1, T - 6), (k * 13.3 + 7.6, 14), (k * 13.3 + 12.3, T - 6)]
            pg.draw.polygon(s.spk, (195, 200, 187), p); pg.draw.polygon(s.spk, (90, 26, 20), p, 1)
        s.bg = pg.Surface((W, H)).convert()
        stops = [(0, (10, 15, 11)), (.75, (28, 38, 26)), (1, (51, 48, 28))]
        for y in range(H):
            f = y / H; (f0, c0), (f1, c1) = (stops[0], stops[1]) if f < .75 else (stops[1], stops[2])
            t = (f - f0) / (f1 - f0)
            pg.draw.line(s.bg, tuple(int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)), (0, y), (W, y))
        v = pg.Surface((96, 52), pg.SRCALPHA)
        for i in range(96):
            for j in range(52):
                d = math.hypot((i - 47.5) / 47.5, (j - 25.5) / 25.5) / 1.4142
                v.set_at((i, j), (0, 0, 0, int(min(1, max(0, (d - .35) / .65)) * 190)))
        s.vig = pg.transform.smoothscale(v, (W, H))
        s.scan = pg.Surface((W, H), pg.SRCALPHA)
        for y in range(0, H, 3): pg.draw.line(s.scan, (0, 0, 0, 34), (0, y), (W, y))
        s.dim = pg.Surface((W, H), pg.SRCALPHA); s.dim.fill((5, 8, 6, 215))
        s.beacon = pg.Surface((60, 200), pg.SRCALPHA)
        for y in range(200): pg.draw.line(s.beacon, (255, 159, 28, int(76 * y / 200)), (0, y), (60, y))
        s.glow = pg.Surface((30, 30), pg.SRCALPHA); pg.draw.circle(s.glow, (255, 176, 46, 60), (15, 15), 15)

    def world(s):
        S, cam, an, P = s.surf, int(round(s.cam)), s.an, s.P
        R = lambda col, x, y, w, h: pg.draw.rect(S, col, (int(x - cam), int(y), int(w), int(h)))
        S.blit(s.bg, (0, 0))
        for sp, col, mh in ((.15, (18, 25, 18), 60), (.35, (13, 19, 13), 20)):
            o = s.cam * sp; k = int(o // 90)
            for i in range(12):
                n = k + i; h = mh + (n * 7919 % 89) * 1.3
                pg.draw.rect(S, col, (int(n * 90 - o), int(440 - h), 72, int(h)))
        for r in range(13):
            for c in range(cam // T, min(cam // T + 26, s.lv['w'])):
                v = s.g[r][c]
                if v == 1: S.blit(s.tl[(r < 11, r > 0 and s.g[r - 1][c] == 1)], (c * T - cam, r * T))
                elif v == 2: S.blit(s.spk, (c * T - cam, r * T))
        fx = s.lv['fl'] * T
        S.blit(s.beacon, (fx - 10 - cam, 6 * T))
        R((154, 160, 143), fx + 18, 8 * T - 6, 4, 3 * T + 6)
        pg.draw.polygon(S, RED, [(fx + 22 - cam, 8 * T - 4), (fx + 54 - cam, 8 * T + 7 + math.sin(an / 6) * 4), (fx + 22 - cam, 8 * T + 18)])
        S.blit(s.fs.render('EXTRACT', 1, AMB), (fx - 6 - cam, 8 * T - 34))
        for o in s.C:
            if o.got: continue
            w = abs(math.cos(an / 18 + o.x)) * 8 + 2; y0 = o.y + math.sin(an / 20 + o.x) * 3; cx = o.x - cam
            S.blit(s.glow, (int(cx - 15), int(y0 - 15)))
            pg.draw.ellipse(S, (255, 194, 60), (int(cx - w), int(y0 - 10), int(2 * w), 20))
            iw = max(1, w - 4); pg.draw.ellipse(S, (185, 122, 12), (int(cx - iw), int(y0 - 6), int(2 * iw), 12))
        for e in s.E:
            if e.dead: continue
            d = e.f or (1 if e.v > 0 else -1); l = math.sin(an / 4) * 3; ex, ey = e.x, e.y
            R((43, 18, 16), ex + 5 + l, ey + 22, 8, 8); R((43, 18, 16), ex + 17 - l, ey + 22, 8, 8)
            R((107, 42, 34), ex + 3, ey + 8, 24, 16)
            pg.draw.circle(S, (28, 31, 26), (int(ex + 15 - cam), int(ey + 8)), 10, draw_top_left=True, draw_top_right=True)
            R((28, 31, 26), ex + 5, ey + 8, 20, 3)
            R((255, 59, 47), ex + (15 if d > 0 else 7), ey + 9, 8, 3)
            R((17, 17, 17), ex + (18 if d > 0 else -2), ey + 16, 14, 4)
            if e.t > 90 - s.cur * 20: R((255, 90, 60), ex + (30 if d > 0 else -6), ey + 14, 8, 8)
        if not (s.inv > 0 and an % 6 < 3):
            f, px, py = P.face, P.x, P.y; l = math.sin(an / 3) * 4 if P.gr and abs(P.vx) > .5 else 0
            R((42, 49, 32), px + 3 + l, py + 24, 7, 10); R((42, 49, 32), px + 12 - l, py + 24, 7, 10)
            R((93, 107, 52), px + 1, py + 10, 20, 16); R((58, 69, 36), px + 4, py + 13, 14, 8)
            pg.draw.circle(S, (47, 56, 32), (int(px + 11 - cam), int(py + 8)), 11, draw_top_left=True, draw_top_right=True)
            R((47, 56, 32), px, py + 7, 22, 3)
            R(AMB, px + (12 if f > 0 else 2), py + 9, 8, 3)
            R((17, 17, 17), px + 12 if f > 0 else px - 12, py + 16, 22, 4)
            if s.cd > 8: R((255, 210, 122), px + 34 if f > 0 else px - 20, py + 14, 8, 8)
        for b in s.eb: R((255, 90, 60), b.x - (8 if b.v > 0 else 0), b.y - 1, 8, 3)
        for b in s.bul: R((255, 233, 168), b.x - (10 if b.v > 0 else 0), b.y - 1, 10, 3)
        for p in s.parts:
            a = max(0, p.l / 30); R(tuple(int(c * a) for c in p.c), p.x, p.y, 4, 4)

    def panel(s, parts, x, y, anchor='l'):
        us = [s.fm.render(t, 1, c) for t, c in parts]
        w = sum(u.get_width() for u in us) + 24; h = us[0].get_height() + 4
        x = x - w if anchor == 'r' else x - w // 2 if anchor == 'c' else x
        bg = pg.Surface((w, h), pg.SRCALPHA); bg.fill((0, 0, 0, 120)); s.scr.blit(bg, (x, y))
        pg.draw.rect(s.scr, AMB, (x, y, 3, h)); xx = x + 14
        for u in us: s.scr.blit(u, (xx, y + 2)); xx += u.get_width()

    def hud(s):
        s.panel([('OP %d/3 // ' % (s.cur + 1), INK), (s.lv['n'].upper(), AMB)], 10, 8)
        s.panel([('COINS ', INK), ('%d/%d' % (s.coins, len(s.C)), AMB), ('    KILLS ', INK), (str(s.kills), AMB)], W // 2, 8, 'c')
        s.panel([('SCORE ', INK), ('%06d' % s.score, AMB)], W - 10, 8, 'r')
        for i in range(3): pg.draw.rect(s.scr, AMB if i < s.hp else (60, 64, 54), (W - 88 + i * 26, 48, 22, 8))
        s.scr.blit(s.fs.render('HP', 1, INK), (W - 118, 42))
        if s.rel > 0:
            u = s.fm.render('RELOADING', 1, AMB); s.scr.blit(u, ((W - u.get_width()) // 2, H - 36))
        else:
            for i in range(6): pg.draw.rect(s.scr, AMB if i < s.ammo else (60, 64, 54), (W // 2 - 48 + i * 16, H - 30, 10, 18))
        for f in s.feed: f[1] -= 1
        s.feed = [f for f in s.feed if f[1] > 0][:5]
        for i, (t, ttl) in enumerate(s.feed):
            u = s.fs.render(t, 1, AMB); u.set_alpha(min(255, ttl * 5)); s.scr.blit(u, (W - 14 - u.get_width(), 84 + i * 22))

    def touch_controls(s):
        if not s.android or s.st != 'play': return
        buttons = ((74, 452, '◀'), (168, 452, '▶'), (730, 452, 'JUMP'), (870, 452, 'FIRE'))
        for x, y, label in buttons:
            pg.draw.circle(s.scr, (14, 18, 13), (x, y), 48)
            pg.draw.circle(s.scr, AMB, (x, y), 48, 3)
            text = s.fs.render(label, 1, AMB)
            s.scr.blit(text, (x - text.get_width() // 2, y - text.get_height() // 2))

    def overlay(s):
        o = s.ov; s.scr.blit(s.dim, (0, 0))
        t = s.fb.render(o['title'], 1, o.get('col', AMB)); s.scr.blit(t, ((W - t.get_width()) // 2, 140))
        y = 235
        for ln in o['lines']:
            u = s.fm.render(ln, 1, DIM); s.scr.blit(u, ((W - u.get_width()) // 2, y)); y += 32
        bw, bh = 330, 48; bx, by = (W - bw) // 2, y + 26
        pg.draw.polygon(s.scr, AMB, [(bx + 12, by), (bx + bw, by), (bx + bw - 12, by + bh), (bx, by + bh)])
        u = s.fm.render(o['btn'] + '  [ENTER]', 1, (17, 17, 17)); s.scr.blit(u, ((W - u.get_width()) // 2, by + (bh - u.get_height()) // 2))

    def draw(s):
        s.an += 1; s.world()
        sx, sy = random.uniform(-.5, .5) * s.shk, random.uniform(-.5, .5) * s.shk; s.shk *= .88
        s.scr.fill((0, 0, 0)); s.scr.blit(s.surf, (int(sx), int(sy)))
        s.scr.blit(s.vig, (0, 0)); s.scr.blit(s.scan, (0, 0))
        s.hud()
        if s.st != 'play': s.overlay()
        else: s.touch_controls()


def main():
    g = Game(); clk = pg.time.Clock()
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit(); return
            g.event(e)
        if g.st == 'play': g.step()
        g.draw(); pg.display.flip(); clk.tick(60)


if __name__ == '__main__':
    main()
