# -*- coding: utf-8 -*-
"""カンプとレンダリング結果の文字インク位置を突き合わせて差分を出す"""
from PIL import Image
import numpy as np, sys
import importlib.util
spec = importlib.util.spec_from_file_location('gen', '/Users/hirano/gyn-page-comp/gen.py')

A = np.asarray(Image.open('/Users/hirano/Downloads/婦人科ページデザイン修正案.jpg').convert('RGB')).astype(float)
B = np.asarray(Image.open('/Users/hirano/gyn-page-comp/render.png').convert('RGB')).astype(float)

ROWS = [
    ('r1', 732, 920, [(99, 419), (452, 769), (801, 1121), (1156, 1475), (1510, 1824)]),
    ('r2', 1085, 1255, [(98, 417), (452, 767), (801, 1119), (1155, 1471), (1510, 1821)]),
    ('r3', 1278, 1457, [(98, 418), (452, 767), (801, 1119)]),
    ('r4', 1612, 1784, [(98, 416), (452, 767), (801, 1119), (1154, 1471), (1510, 1821)]),
    ('r5', 1932, 2063, [(97, 413), (443, 763), (794, 1106), (1135, 1464), (1496, 1819)]),
    ('r6', 2078, 2210, [(96, 413), (443, 763), (793, 1105), (1135, 1465), (1495, 1819)]),
    ('r7', 2344, 2444, [(98, 405), (444, 763)]),
    ('r8', 2578, 2694, [(98, 485), (520, 911), (953, 1345), (1383, 1770)]),
    ('r9', 2818, 2934, [(98, 451), (494, 857), (898, 1272)]),
]


def ink(img, x0, y0, x1, y1, thr=640, sat=40):
    reg = img[y0:y1, x0:x1]
    m = ((reg.max(axis=2) - reg.min(axis=2)) <= sat) & (reg.sum(axis=2) < thr)
    ys = np.where(m.any(axis=1))[0]
    xs = np.where(m.any(axis=0))[0]
    if len(ys) == 0:
        return None
    return (x0 + xs[0], y0 + ys[0], x0 + xs[-1], y0 + ys[-1])


print('%-9s %-6s %-22s %-22s %s' % ('row', 'card', 'comp(cx,cy,w,h)', 'render', 'delta'))
for rid, t, b, cards in ROWS:
    for i, (x0, x1) in enumerate(cards):
        # 文字はカード下半分 or 右半分にある。ざっくり全体から無彩色インクを取る
        pa = ink(A, x0 + 12, t + 12, x1 - 12, b - 12)
        pb = ink(B, x0 + 12, t + 12, x1 - 12, b - 12)
        if not pa or not pb:
            continue
        fa = ((pa[0] + pa[2]) / 2, (pa[1] + pa[3]) / 2, pa[2] - pa[0], pa[3] - pa[1])
        fb = ((pb[0] + pb[2]) / 2, (pb[1] + pb[3]) / 2, pb[2] - pb[0], pb[3] - pb[1])
        d = tuple(round(y - x, 1) for x, y in zip(fa, fb))
        print('%-9s %-6d %-22s %-22s %s' % (rid, i, fa, fb, d))
