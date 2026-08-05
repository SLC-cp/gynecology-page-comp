# -*- coding: utf-8 -*-
"""2枚目のカンプ(IMG_4687.JPG)から診療アイコン37個を透過PNGで書き出し、
   本番テーマ sakuratheme/assets/images/gyne/ico/ に配置する。"""
from PIL import Image
import numpy as np, os

SRC = '/Users/hirano/Downloads/IMG_4687.JPG'
DEST = '/Users/hirano/Downloads/sakuratheme/assets/images/gyne/ico'
os.makedirs(DEST, exist_ok=True)

A = np.asarray(Image.open(SRC).convert('RGB')).astype(float)

BOXES = [
    [(116, 76, 73, 70), (302, 76, 81, 70), (498, 80, 64, 59), (686, 80, 60, 59), (880, 82, 59, 63)],
    [(128, 266, 47, 50), (326, 266, 33, 50), (504, 268, 52, 47), (680, 266, 72, 50), (890, 266, 34, 50)],
    [(116, 374, 68, 58), (307, 370, 69, 53), (490, 378, 79, 54)],
    [(124, 546, 54, 49), (318, 552, 46, 40), (502, 546, 54, 50), (688, 546, 56, 48), (882, 545, 42, 51)],
    [(128, 698, 46, 46), (312, 699, 53, 46), (518, 698, 22, 47), (694, 698, 40, 48), (880, 700, 48, 46)],
    [(128, 792, 47, 46), (314, 792, 51, 44), (506, 796, 44, 40), (687, 792, 57, 42), (876, 794, 55, 38)],
    [(94, 936, 34, 42), (276, 938, 40, 36)],
    [(102, 1040, 29, 38), (300, 1040, 49, 38), (565, 1044, 33, 29), (788, 1044, 36, 30)],
    [(92, 1141, 40, 41), (314, 1144, 52, 38), (556, 1146, 42, 30)],
]
LABELS = [
    ['超低用量ピル', '低用量ピル', 'ミニピル', 'アフターピル', 'ミレーナ'],
    ['生理不順', '生理痛', 'PMS（月経前症候群）', '生理がこない（無月経）', '不正出血'],
    ['視床下部性無月経', '多のう胞性卵巣（PCOS）', '子宮内膜症'],
    ['おりものの異常', '外陰部のかゆみ', 'カンジダ膣炎', '細菌性膣症', 'バルトリン腺嚢腫'],
    ['クラミジア', '淋病', '梅毒', 'HIV', '性器ヘルペス'],
    ['コンジローマ', 'ウレアプラズマ', 'マイコプラズマ', 'B型肝炎', 'C型肝炎'],
    ['妊娠', '人工妊娠中絶'],
    ['婦人科検診', '子宮頸がん検診', 'HPVワクチン', 'ブライダルチェック'],
    ['膀胱炎', '子宮筋腫', '卵巣嚢腫'],
]

SCALE = 2          # 2倍で書き出し（表示は等倍〜1.3倍を想定）
n = 0
lines = []
for row, labs in zip(BOXES, LABELS):
    for (x, y, w, h), lab in zip(row, labs):
        n += 1
        pad = 5
        crop = A[y - pad:y + h + pad, x - pad:x + w + pad]
        # 地色はアイコンの上辺と左右から採り、最も明るい側（75パーセンタイル）を採用する。
        # 横並びカードでは右側に文字が来るため、中央値だと文字を拾って縁が残る。
        ring = [A[yy, xx] for yy in range(max(0, y - 14), max(1, y - 7))
                for xx in range(x - 6, x + w + 6) if 0 <= xx < A.shape[1]]
        ring += [A[yy, x + dx] for yy in range(y, y + h)
                 for dx in (-20, -16) if 0 <= x + dx < A.shape[1]]
        ring = np.array(ring)
        light = ring[ring.mean(axis=1) > 200]      # 文字やアイコンの画素を除外
        BG = np.median(light if len(light) > 20 else ring, axis=0)
        alpha = 1.0 - (crop / np.maximum(BG, 1)).min(axis=2)
        # 地色推定の誤差でうっすら四角が残るのを防ぐ（ごく薄い部分は完全透明に）
        alpha = np.clip((alpha - 0.10) / 0.90, 0, 1)
        a3 = np.maximum(alpha, 1e-6)[:, :, None]
        C = np.clip((crop - BG * (1 - a3)) / a3, 0, 255)
        rgba = np.zeros(crop.shape[:2] + (4,), np.uint8)
        rgba[:, :, :3] = C.round().astype(np.uint8)
        rgba[:, :, 3] = (alpha * 255).round().astype(np.uint8)
        img = Image.fromarray(rgba)
        img = img.resize((img.width * SCALE, img.height * SCALE), Image.LANCZOS)
        name = 'ic-%02d.png' % n
        img.save(os.path.join(DEST, name))
        lines.append('%s  %s  %dx%d' % (name, lab, img.width, img.height))
print('\n'.join(lines))
print('計 %d 個 → %s' % (n, DEST))
