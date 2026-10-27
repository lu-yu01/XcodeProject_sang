"""Seven independent visual carriers for the 2026 varied-operation exercise.

All scene values describe printed information.  The second transformer deliberately
uses inverse lookups / edge predicates instead of the first transformer's mutations.
"""
from __future__ import annotations

import copy
import itertools
import json
import math
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont


def _clone(scene):
    return copy.deepcopy(scene)


def _normal(scene):
    s = _clone(scene)
    if s['kind'] == 1:
        s['edges'] = sorted(s['edges'])
    return s


def scene_key(scene):
    """Canonical visible scene: no seeds, derivations, answers or hidden attributes."""
    return json.dumps(_normal(scene), ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def _edge_relabel(edges, fn):
    out = []
    for a, b, direct, dash in edges:
        start, end = (a, b) if direct == 0 else (b, a)
        start, end = fn(start), fn(end)
        out.append([min(start, end), max(start, end), int(start > end), dash])
    return sorted(out)


def apply(scene, opid):
    s = _clone(scene)
    k = s['kind']
    prefix, op = opid.split('_', 1)
    if prefix != f'N{k}':
        raise ValueError((k, opid))
    if k == 1:
        if op == 'reverse':
            for e in s['edges']:
                e[2] ^= 1
        elif op == 'marker':
            s['marker'] = (s['marker'] + 1) % 5
        elif op == 'dash':
            for e in s['edges']:
                e[3] ^= 1
        elif op == 'incident':
            for e in s['edges']:
                if s['marker'] in e[:2]:
                    e[2] ^= 1
        elif op == 'cycle':
            s['edges'] = _edge_relabel(s['edges'], lambda v: (v + 1) % 5)
        elif op == 'reflect':
            s['edges'] = _edge_relabel(s['edges'], lambda v: (-v) % 5)
            s['marker'] = (-s['marker']) % 5
        else:
            raise ValueError(opid)
    elif k == 2:
        if op == 'height':
            s['y'] = [4 - y for y in s['y']]
        elif op == 'cycle':
            s['y'] = s['y'][-1:] + s['y'][:-1]
        elif op == 'ends':
            s['y'][0], s['y'][4] = s['y'][4], s['y'][0]
        elif op == 'inner':
            s['y'][1], s['y'][3] = s['y'][3], s['y'][1]
        elif op == 'ascending':
            for i in range(4):
                if s['y'][i + 1] > s['y'][i]:
                    s['dash'][i] ^= 1
        elif op == 'style':
            s['dash'] = list(reversed(s['dash']))
        else:
            raise ValueError(opid)
    elif k == 3:
        if op == 'all':
            s['dash'] = [1 - d for d in s['dash']]
        elif op == 'horizontal':
            for i in (0, 1, 6):
                s['dash'][i] ^= 1
        elif op == 'direction':
            old = s['dash'][:]
            for a, b in zip((0, 6, 1, 2, 3, 8, 7, 5, 4), (2, 3, 8, 7, 5, 4, 0, 6, 1)):
                s['dash'][b] = old[a]
        elif op == 'mirror':
            old = s['dash'][:]
            for a, b in ((0, 1), (2, 4), (3, 5), (7, 8)):
                s['dash'][a], s['dash'][b] = old[b], old[a]
        elif op == 'inner':
            old = s['dash'][:]
            for a, b in ((6, 8), (8, 7), (7, 6)):
                s['dash'][b] = old[a]
        elif op == 'exchange':
            for a, b in ((0, 7), (1, 8)):
                s['dash'][a], s['dash'][b] = s['dash'][b], s['dash'][a]
        else:
            raise ValueError(opid)
    elif k == 4:
        if op == 'top':
            for key in ('to', 'dash'):
                s[key] = s[key][-1:] + s[key][:-1]
        elif op == 'bottom':
            s['to'] = [(v + 1) % 4 for v in s['to']]
        elif op == 'outer':
            s['to'] = [{0: 3, 3: 0}.get(v, v) for v in s['to']]
        elif op == 'left':
            for i, dest in enumerate(s['to']):
                if dest < 2:
                    s['dash'][i] ^= 1
        elif op == 'ends':
            for key in ('to', 'dash'):
                s[key][0], s[key][3] = s[key][3], s[key][0]
        elif op == 'mirror':
            s['to'] = [3 - v for v in s['to']]
        else:
            raise ValueError(opid)
    elif k == 5:
        if op == 'length':
            s['length'] = s['length'][-1:] + s['length'][:-1]
        elif op == 'style':
            s['dash'] = s['dash'][-1:] + s['dash'][:-1]
        elif op == 'complement':
            s['length'] = [5 - v for v in s['length']]
        elif op == 'long':
            for i, v in enumerate(s['length']):
                if v >= 3:
                    s['dash'][i] ^= 1
        elif op == 'point':
            s['mark'] = s['mark'][-1:] + s['mark'][:-1]
        elif op == 'ends':
            s['length'][0], s['length'][4] = s['length'][4], s['length'][0]
        else:
            raise ValueError(opid)
    elif k == 6:
        if op == 'length':
            s['length'] = s['length'][-1:] + s['length'][:-1]
        elif op == 'tip':
            s['tip'] = s['tip'][1:] + s['tip'][:1]
        elif op == 'black':
            for i, v in enumerate(s['tip']):
                if v == 1:
                    s['dash'][i] ^= 1
        elif op == 'complement':
            s['length'] = [4 - v for v in s['length']]
        elif op == 'shape':
            s['tip'] = [{0: 0, 1: 2, 2: 1}[v] for v in s['tip']]
        elif op == 'pair':
            s['length'][0], s['length'][3] = s['length'][3], s['length'][0]
        else:
            raise ValueError(opid)
    elif k == 7:
        if op == 'xor':
            s['a'] ^= s['b']
        elif op == 'union':
            s['b'] |= s['a']
        elif op == 'swap':
            s['a'], s['b'] = s['b'], s['a']
        elif op == 'rotate':
            mp = (6, 5, 4, 3, 2, 1, 0)
            for key in ('a', 'b'):
                old = s[key]
                s[key] = sum(((old >> i) & 1) << mp[i] for i in range(7))
        elif op == 'mirror':
            mp = (0, 2, 1, 3, 5, 4, 6)
            old = s['a']
            s['a'] = sum(((old >> i) & 1) << mp[i] for i in range(7))
        elif op == 'middle':
            s['b'] ^= 1 << 3
        else:
            raise ValueError(opid)
    else:
        raise ValueError(k)
    return _normal(s)


def independent_apply(scene, opid):
    """Separate inverse-lookup / Boolean-form implementation, never calls apply."""
    src = _clone(scene)
    out = _clone(scene)
    k = src['kind']
    prefix, op = opid.split('_', 1)
    if prefix != f'N{k}':
        raise ValueError((k, opid))
    if k == 1:
        out['marker'] = ((src['marker'] + 1) % 5 if op == 'marker' else
                         (-src['marker']) % 5 if op == 'reflect' else src['marker'])
        records = {}
        for low, high, direct, style in src['edges']:
            records[(low, high)] = ((low, high) if direct == 0 else (high, low), style)
        out['edges'] = []
        inv = lambda n: ((n - 1) % 5 if op == 'cycle' else (-n) % 5 if op == 'reflect' else n)
        for a, b in itertools.combinations(range(5), 2):
            old_a, old_b = inv(a), inv(b)
            rec = records.get(tuple(sorted((old_a, old_b))))
            if rec is None:
                continue
            (u, v), dash = rec
            forward = u == old_a
            if op == 'reverse' or (op == 'incident' and src['marker'] in (old_a, old_b)):
                forward = not forward
            if op == 'dash':
                dash = 1 - dash
            out['edges'].append([a, b, int(not forward), dash])
        if op not in ('reverse', 'marker', 'dash', 'incident', 'cycle', 'reflect'):
            raise ValueError(opid)
    elif k == 2:
        h, d = src['y'], src['dash']
        if op == 'height':
            out['y'] = [abs(v - 4) for v in h]
        elif op == 'cycle':
            out['y'] = [h[(j - 1) % 5] for j in range(5)]
        elif op in ('ends', 'inner'):
            indices = (4, 1, 2, 3, 0) if op == 'ends' else (0, 3, 2, 1, 4)
            out['y'] = [h[j] for j in indices]
        elif op == 'ascending':
            out['dash'] = [int(bool(d[j]) != (h[j] < h[j + 1])) for j in range(4)]
        elif op == 'style':
            out['dash'] = [d[3 - j] for j in range(4)]
        else:
            raise ValueError(opid)
    elif k == 3:
        old = src['dash']
        if op in ('all', 'horizontal'):
            targets = set(range(9)) if op == 'all' else {0, 1, 6}
            out['dash'] = [int(bool(v) != (j in targets)) for j, v in enumerate(old)]
        else:
            # Each entry says which old segment supplies the new printed segment.
            inverses = {
                'direction': (7, 4, 0, 6, 8, 3, 5, 2, 1),
                'mirror': (1, 0, 4, 5, 2, 3, 6, 8, 7),
                'inner': (0, 1, 2, 3, 4, 5, 7, 8, 6),
                'exchange': (7, 8, 2, 3, 4, 5, 6, 0, 1),
            }
            out['dash'] = [old[i] for i in inverses[op]]
    elif k == 4:
        p, d = src['to'], src['dash']
        if op in ('top', 'ends'):
            indices = (3, 0, 1, 2) if op == 'top' else (3, 1, 2, 0)
            out['to'], out['dash'] = [[v[i] for i in indices] for v in (p, d)]
        elif op == 'left':
            out['dash'] = [int(bool(d[i]) != (p[i] in (0, 1))) for i in range(4)]
        elif op == 'bottom':
            out['to'] = [(v - 3) % 4 for v in p]
        elif op == 'outer':
            out['to'] = [3 - v if v in (0, 3) else v for v in p]
        elif op == 'mirror':
            out['to'] = [abs(v - 3) for v in p]
        else:
            raise ValueError(opid)
    elif k == 5:
        if op in ('length', 'style', 'point'):
            field = {'length': 'length', 'style': 'dash', 'point': 'mark'}[op]
            out[field] = [src[field][(i + 4) % 5] for i in range(5)]
        elif op == 'complement':
            out['length'] = [abs(v - 5) for v in src['length']]
        elif op == 'long':
            out['dash'] = [int(bool(v) != (src['length'][i] in (3, 4))) for i, v in enumerate(src['dash'])]
        elif op == 'ends':
            out['length'] = [src['length'][i] for i in (4, 1, 2, 3, 0)]
        else:
            raise ValueError(opid)
    elif k == 6:
        if op == 'length':
            out['length'] = [src['length'][(i + 5) % 6] for i in range(6)]
        elif op == 'tip':
            out['tip'] = [src['tip'][(i + 1) % 6] for i in range(6)]
        elif op == 'black':
            out['dash'] = [int(bool(v) != (src['tip'][i] == 1)) for i, v in enumerate(src['dash'])]
        elif op == 'complement':
            out['length'] = [abs(v - 4) for v in src['length']]
        elif op == 'shape':
            out['tip'] = [0 if v == 0 else 3 - v for v in src['tip']]
        elif op == 'pair':
            out['length'] = [src['length'][i] for i in (3, 1, 2, 0, 4, 5)]
        else:
            raise ValueError(opid)
    elif k == 7:
        a = [(src['a'] >> i) & 1 for i in range(7)]
        b = [(src['b'] >> i) & 1 for i in range(7)]
        if op == 'xor':
            a = [int(x != y) for x, y in zip(a, b)]
        elif op == 'union':
            b = [int(x or y) for x, y in zip(a, b)]
        elif op == 'swap':
            a, b = b, a
        elif op == 'rotate':
            a, b = a[::-1], b[::-1]
        elif op == 'mirror':
            a = [a[i] for i in (0, 2, 1, 3, 5, 4, 6)]
        elif op == 'middle':
            b[3] = int(not b[3])
        else:
            raise ValueError(opid)
        out['a'] = sum(v * 2**i for i, v in enumerate(a))
        out['b'] = sum(v * 2**i for i, v in enumerate(b))
    else:
        raise ValueError(k)
    return _normal(out)


@lru_cache(maxsize=20)
def _font(size):
    return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', size)


class _Painter:
    def __init__(self, size):
        self.scale = 3 * size / 280
        self.im = Image.new('RGB', (size * 3, size * 3), 'white')
        self.d = ImageDraw.Draw(self.im)

    def p(self, pt):
        return tuple(round(x * self.scale) for x in pt)

    def line(self, a, b, width=2.4, dash=False, fill='black'):
        if not dash:
            self.d.line([self.p(a), self.p(b)], fill=fill, width=max(1, round(width * self.scale)))
            return
        length = math.dist(a, b)
        if length < 0.01:
            return
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        t = 0.0
        while t < length:
            q = min(length, t + 7)
            self.d.line([self.p((a[0] + ux * t, a[1] + uy * t)), self.p((a[0] + ux * q, a[1] + uy * q))], fill=fill, width=max(1, round(width * self.scale)))
            t += 11

    def circle(self, xy, radius=4, black=False, width=1.6):
        x, y = xy
        self.d.ellipse([self.p((x - radius, y - radius)), self.p((x + radius, y + radius))], fill='black' if black else 'white', outline='black', width=max(1, round(width * self.scale)))

    def text(self, xy, value, size=15, anchor='mm'):
        self.d.text(self.p(xy), value, font=_font(round(size * self.scale)), fill='black', anchor=anchor)

    def arrow(self, a, b, at=.55, size=7):
        theta = math.atan2(b[1] - a[1], b[0] - a[0])
        x, y = a[0] + (b[0] - a[0]) * at, a[1] + (b[1] - a[1]) * at
        p1 = (x - size * math.cos(theta - .46), y - size * math.sin(theta - .46))
        p2 = (x - size * math.cos(theta + .46), y - size * math.sin(theta + .46))
        self.d.polygon([self.p((x, y)), self.p(p1), self.p(p2)], fill='black')

    def done(self, size):
        return self.im.resize((size, size), Image.Resampling.LANCZOS)


_TRUSS_PTS = ((35, 235), (140, 235), (245, 235), (87.5, 144), (192.5, 144), (140, 53))
_TRUSS_EDGES = ((0, 1), (1, 2), (0, 3), (3, 5), (2, 4), (4, 5), (3, 4), (3, 1), (4, 1))


def render_panel(scene, size=280):
    s = scene
    p = _Painter(size)
    k = s['kind']
    if k == 1:
        pts = [(140 + 102 * math.sin(2 * math.pi * i / 5), 142 - 102 * math.cos(2 * math.pi * i / 5)) for i in range(5)]
        for a, b, direct, dash in s['edges']:
            p.line(pts[a], pts[b], dash=bool(dash))
            start, end = (pts[a], pts[b]) if not direct else (pts[b], pts[a])
            p.arrow(start, end, at=.57, size=8.5)
        for i, xy in enumerate(pts):
            p.circle(xy, 8, black=(i == s['marker']), width=1.8)
            vx, vy = xy[0] - 140, xy[1] - 142
            norm = math.hypot(vx, vy)
            p.text((xy[0] + 21 * vx / norm, xy[1] + 21 * vy / norm), str(i + 1), 16)
    elif k == 2:
        pts = [(38 + i * 51, 235 - s['y'][i] * 47.5) for i in range(5)]
        for i in range(4):
            p.line(pts[i], pts[i + 1], width=2.8, dash=bool(s['dash'][i]))
        for i, xy in enumerate(pts):
            p.circle(xy, 4 if i not in (0, 4) else 6.5, black=i == 0, width=1.6)
        # Five tiny fixed base ticks establish equal-spaced horizontal positions.
        for i in range(5):
            p.line((38 + 51 * i, 250), (38 + 51 * i, 255), width=1.2)
    elif k == 3:
        for i, (a, b) in enumerate(_TRUSS_EDGES):
            p.line(_TRUSS_PTS[a], _TRUSS_PTS[b], width=2.6, dash=bool(s['dash'][i]))
        for xy in _TRUSS_PTS:
            p.circle(xy, 3.3, black=True)
    elif k == 4:
        xs = (38, 106, 174, 242)
        for i, dest in enumerate(s['to']):
            p.line((xs[i], 65), (xs[dest], 214), width=2.7, dash=bool(s['dash'][i]))
        for i in range(4):
            p.circle((xs[i], 65), 5.5, black=False)
            p.circle((xs[i], 214), 5.5, black=False)
            p.text((xs[i], 42), str(i + 1), 16)
            p.text((xs[i], 238), '甲乙丙丁'[i], 16)
    elif k == 5:
        for i, (length, dash, mark) in enumerate(zip(s['length'], s['dash'], s['mark'])):
            y = 47 + i * 46
            p.line((43, y), (43 + length * 46, y), width=3, dash=bool(dash))
            p.circle((43, y), 6, black=bool(mark), width=1.7)
            p.line((43 + length * 46, y - 5), (43 + length * 46, y + 5), width=2.3)
    elif k == 6:
        center = (140, 140)
        for i, (length, tip, dash) in enumerate(zip(s['length'], s['tip'], s['dash'])):
            angle = -math.pi / 2 + i * math.pi / 3
            r = 40 + 24 * length
            xy = (140 + r * math.cos(angle), 140 + r * math.sin(angle))
            p.line(center, xy, width=2.8, dash=bool(dash))
            if tip < 2:
                p.circle(xy, 6.5, black=tip == 1, width=1.7)
            else:
                # Radial triangle points outwards; triangle shape, not orientation, is data.
                tri = [(xy[0] + 8 * math.cos(angle + delta), xy[1] + 8 * math.sin(angle + delta)) for delta in (0, 2.25, -2.25)]
                p.d.polygon([p.p(v) for v in tri], fill='black')
        p.circle(center, 4, black=True)
    elif k == 7:
        for x, name, value in ((32, '甲', s['a']), (169, '乙', s['b'])):
            segs = (((x, 70), (x + 75, 70)), ((x, 70), (x, 140)), ((x + 75, 70), (x + 75, 140)), ((x, 140), (x + 75, 140)), ((x, 140), (x, 210)), ((x + 75, 140), (x + 75, 210)), ((x, 210), (x + 75, 210)))
            for i, (a, b) in enumerate(segs):
                if value & (1 << i):
                    p.line(a, b, width=4)
            # Fixed dots define the seven segment locations even if a segment is absent.
            for xx, yy in ((x, 70), (x + 75, 70), (x, 140), (x + 75, 140), (x, 210), (x + 75, 210)):
                p.circle((xx, yy), 2.7, black=True)
            p.text((x + 37.5, 41), name, 17)
    else:
        raise ValueError(k)
    return p.done(size)


def _run(scene, chain, fn=apply):
    current = _clone(scene)
    for op in chain:
        current = fn(current, op)
    return current


def _candidate(k, rng):
    bit = lambda n: [rng.randrange(2) for _ in range(n)]
    if k == 1:
        pairs = list(itertools.combinations(range(5), 2))
        rng.shuffle(pairs)
        edges = [[a, b, rng.randrange(2), rng.randrange(2)] for a, b in pairs[:5]]
        return {'kind': 1, 'marker': rng.randrange(5), 'edges': sorted(edges)}
    if k == 2:
        y = list(range(5))
        rng.shuffle(y)
        return {'kind': 2, 'y': y, 'dash': bit(4)}
    if k == 3:
        return {'kind': 3, 'dash': bit(9)}
    if k == 4:
        to = list(range(4))
        rng.shuffle(to)
        return {'kind': 4, 'to': to, 'dash': bit(4)}
    if k == 5:
        return {'kind': 5, 'length': [rng.randint(1, 4) for _ in range(5)], 'dash': bit(5), 'mark': bit(5)}
    if k == 6:
        return {'kind': 6, 'length': [rng.randint(1, 3) for _ in range(6)], 'tip': [rng.randrange(3) for _ in range(6)], 'dash': bit(6)}
    if k == 7:
        return {'kind': 7, 'a': rng.randint(1, 126), 'b': rng.randint(1, 126)}
    raise ValueError(k)


def _decoy_keys(source, chain, rules):
    correct = scene_key(_run(source, chain))
    keys = set()
    for j in range(len(chain)):
        for r in rules:
            alt = chain[:]
            alt[j] = r['id']
            key = scene_key(_run(source, alt))
            if key != correct:
                keys.add(key)
    for j in range(len(chain) - 1):
        alt = chain[:]
        alt[j], alt[j + 1] = alt[j + 1], alt[j]
        key = scene_key(_run(source, alt))
        if key != correct:
            keys.add(key)
    return keys


def _usable(source, chain, rules):
    final = _run(source, chain)
    current = source
    for op in chain:
        other = apply(current, op)
        if scene_key(other) == scene_key(current):
            return False
        if scene_key(other) != scene_key(independent_apply(current, op)):
            raise AssertionError(('independent mismatch', source['kind'], op, current))
        current = other
    for j in range(len(chain)):
        if scene_key(_run(source, chain[:j] + chain[j + 1:])) == scene_key(final):
            return False
    # Every question includes a consequential order-sensitive adjacent pair.
    order_sensitive = False
    for j in range(len(chain) - 1):
        alt = chain[:]
        alt[j], alt[j + 1] = alt[j + 1], alt[j]
        if scene_key(_run(source, alt)) != scene_key(final):
            order_sensitive = True
    if not order_sensitive or len(_decoy_keys(source, chain, rules)) < 5:
        return False
    if source['kind'] == 7:
        # Avoid nearly empty / nearly full LED panels in source and answer.
        for panel in (source, final):
            if not all(2 <= panel[f].bit_count() <= 5 for f in ('a', 'b')):
                return False
    return True


def _rules(k, rows):
    return [{'id': f'N{k}_{name}', 'code': code, 'text': text} for name, code, text in rows]


def get_groups():
    specs = [
        (1, '有向线网：节点与箭头',
         '五个节点和编号位置固定，编号沿顺时针递增；黑节点为选中点。交叉处不连通，未提及的属性均不变。',
         [('reverse', '↶', '所有线段的箭头均反向。'),
          ('marker', 'P', '黑节点沿编号顺序移后一位，5之后为1。'),
          ('dash', 'D', '所有连线实线与虚线互换。'),
          ('incident', 'I', '仅把与当前黑节点相连的箭头反向。'),
          ('cycle', 'C', '所有连线两端编号均加1，5之后为1；黑节点不动。'),
          ('reflect', 'M', '沿穿过节点1的竖轴翻转连线及黑节点，编号不动。')],
         [('marker', 'incident'), ('dash', 'cycle', 'incident'), ('reflect', 'marker', 'incident', 'reverse')]),
        (2, '折线路径：高度与线型',
         '折线五个顶点按从左到右排列，横向间距和五档高度固定；只移动高度时，不改变各段线型。左黑、右空心端点固定。',
         [('height', 'V', '五个顶点高度上下翻转。'),
          ('cycle', 'H', '五个顶点高度依次右移一位，最右高度移到最左。'),
          ('ends', 'E', '只交换最左与最右顶点的高度。'),
          ('inner', 'J', '只交换从左数第2与第4个顶点的高度。'),
          ('ascending', 'U', '仅将从左向右上升的线段作实虚互换。'),
          ('style', 'S', '四段线型顺序左右倒置，顶点不动。')],
         [('cycle', 'ascending'), ('height', 'cycle', 'ascending'), ('style', 'ends', 'inner', 'ascending')]),
        (3, '三角构架：方向族与内外边',
         '构架位置固定，由四个等边小三角形组成。方向族指三条水平线、三条左下至右上线、三条左上至右下线；每族按中点从左到右编号。',
         [('all', 'F', '全部九条线实虚互换。'),
          ('horizontal', 'H', '仅三条水平线实虚互换。'),
          ('direction', 'C', '三方向族线型按水平→右上斜→右下斜循环，同序号对应。'),
          ('mirror', 'M', '全部线型沿构架竖直中轴左右翻转。'),
          ('inner', 'T', '中心倒三角线型按上边→右边→左边循环。'),
          ('exchange', 'X', '底边左、右两段分别与中心倒三角的左、右斜边交换线型。')],
         [('horizontal', 'direction'), ('mirror', 'inner', 'horizontal'), ('all', 'exchange', 'direction', 'horizontal')]),
        (4, '双排接线：端口与连接',
         '上下两排端口位置及标记固定，每个上端口恰连一个下端口。交叉处不连通；端点移动时，线型随该条线一起移动。',
         [('top', 'U', '四条线的上端点依次右移，4的端点移至1。'),
          ('bottom', 'B', '四条线的下端点按甲乙丙丁循环移后一位。'),
          ('outer', 'E', '只交换下端点甲、丁所接的两条线。'),
          ('left', 'D', '仅将下端点接甲或乙的线作实虚互换。'),
          ('ends', 'X', '只交换上端点1、4所接的两条线。'),
          ('mirror', 'M', '所有下端点左右翻转，上端点不动。')],
         [('bottom', 'left'), ('top', 'outer', 'left'), ('mirror', 'ends', 'bottom', 'left')]),
        (5, '平行线束：长度与端点',
         '五条水平线左端对齐，自上而下排列；长度为1—4个等长单位。空心或实心圆属于该行，未提及的属性不动。',
         [('length', 'L', '五行长度依次下移一行，最下行长度移到最上行。'),
          ('style', 'S', '五行线型依次下移一行，最下行线型移到最上行。'),
          ('complement', 'C', '每行长度改为5减去原长度。'),
          ('long', 'D', '仅把长度为3或4单位的行作实虚互换。'),
          ('point', 'P', '五行圆点样式依次下移一行，最下行移到最上行。'),
          ('ends', 'E', '只交换第1行与第5行的长度。')],
         [('length', 'long'), ('complement', 'style', 'long'), ('point', 'ends', 'length', 'long')]),
        (6, '辐射线段：长度与端饰',
         '六条射线方向固定，从正上方开始顺时针编号1—6；长度分三档。端饰为空心圆、实心圆或实心三角，三角尖端始终朝外。',
         [('length', 'L', '六条射线的长度依次顺时针移一位。'),
          ('tip', 'T', '六个端饰依次逆时针移一位，长度与线型不动。'),
          ('black', 'D', '仅将端饰为实心圆的射线作实虚互换。'),
          ('complement', 'C', '最长、最短两档互换，中档不变。'),
          ('shape', 'S', '实心圆与实心三角互换，空心圆不变。'),
          ('pair', 'E', '只交换正上与正下两条射线的长度。')],
         [('tip', 'black'), ('shape', 'tip', 'black'), ('complement', 'pair', 'length', 'black')]),
        (7, '双线框：集合运算与位置',
         '甲、乙各有七段潜在线位，上中下三横线与左右各两竖线；六个定位点始终保留。运算按对应线位进行，未提及的图不变。',
         [('xor', '⊕', '甲改为甲乙对应线段去同存异所得图。'),
          ('union', '∪', '乙改为甲乙全部线段合并所得图。'),
          ('swap', '⇄', '甲乙两图互换。'),
          ('rotate', 'R', '甲乙两图均旋转180°，定位点不动。'),
          ('mirror', 'M', '仅甲图左右翻转。'),
          ('middle', 'T', '仅乙图中间横线作有无互换。')],
         [('middle', 'xor'), ('mirror', 'swap', 'xor'), ('rotate', 'union', 'swap', 'xor')]),
    ]
    groups = []
    for k, title, intro, rows, chains in specs:
        rules = _rules(k, rows)
        rng = random.Random(2026102700 + k)
        questions = []
        used = set()
        for names in chains:
            chain = [f'N{k}_{name}' for name in names]
            for attempt in range(100000):
                source = _candidate(k, rng)
                if scene_key(source) not in used and _usable(source, chain, rules):
                    used.add(scene_key(source))
                    questions.append({'source': source, 'chain': chain})
                    break
            else:
                raise RuntimeError(('no useful source', k, chain))
        groups.append({'id': k, 'title': title, 'intro': intro, 'rules': rules, 'questions': questions})
    return groups


def self_audit():
    groups = get_groups()
    summary = {'group_count': len(groups), 'question_count': sum(len(g['questions']) for g in groups), 'groups': [], 'errors': []}
    rng = random.Random(2026102729)
    for group in groups:
        k = group['id']
        seen = set()
        rows = []
        for qidx, q in enumerate(group['questions'], 1):
            original = scene_key(q['source'])
            assert _usable(q['source'], q['chain'], group['rules'])
            assert scene_key(q['source']) == original
            seen.update(q['chain'])
            rows.append({'question': qidx, 'steps': len(q['chain']), 'distinct_decoys': len(_decoy_keys(q['source'], q['chain'], group['rules'])), 'all_steps_effective': True, 'every_step_necessary': True, 'order_sensitive': True})
        assert seen == {r['id'] for r in group['rules']}
        # Reach many off-chain scenes, so independence does not only verify the answer path.
        checks = 0
        for _ in range(250):
            src = _candidate(k, rng)
            for rule in group['rules']:
                frozen = scene_key(src)
                assert scene_key(apply(src, rule['id'])) == scene_key(independent_apply(src, rule['id'])), (k, rule, src)
                assert scene_key(src) == frozen
                checks += 1
        summary['groups'].append({'id': k, 'title': group['title'], 'rules': len(group['rules']), 'complete_rule_coverage': True, 'independent_checks': checks, 'questions': rows})
    return summary


if __name__ == '__main__':
    import pathlib
    report = self_audit()
    destination = pathlib.Path(__file__).with_name('lines_audit.json')
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
