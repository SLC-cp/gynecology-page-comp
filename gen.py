# -*- coding: utf-8 -*-
"""婦人科ページデザイン修正案.jpg を単一HTMLに再現するジェネレータ.
   カンプから座標・色を実測し、アイコン等はアルファ付きPNGで切り出して base64 埋め込みする。
"""
from PIL import Image
import numpy as np, base64, io, json, os

SRC = '/Users/hirano/Downloads/婦人科ページデザイン修正案.jpg'
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(OUT_DIR, 'assets')
os.makedirs(ASSETS, exist_ok=True)

im = Image.open(SRC).convert('RGB')
A = np.asarray(im).astype(float)
PAGE_BG = np.array([254., 250., 251.])
W, H = im.size

# ---------------------------------------------------------------- utilities
def runs(mask, minlen=1):
    out, s = [], None
    for i, v in enumerate(mask):
        if v and s is None:
            s = i
        elif not v and s is not None:
            if i - s >= minlen:
                out.append((s, i - 1))
            s = None
    if s is not None and len(mask) - s >= minlen:
        out.append((s, len(mask) - 1))
    return out


def b64(path):
    ext = 'png' if path.endswith('.png') else 'jpeg'
    with open(path, 'rb') as f:
        return 'data:image/%s;base64,%s' % (ext, base64.b64encode(f.read()).decode())


def save_png(arr_rgba, name):
    p = os.path.join(ASSETS, name)
    Image.fromarray(arr_rgba, 'RGBA').save(p)
    return p


def save_jpg(img, name, q=92):
    p = os.path.join(ASSETS, name)
    img.save(p, quality=q, subsampling=0)
    return p


def inpaint_h(arr, x0, y0, x1, y1):
    """[x0,x1) x [y0,y1) を左右の外側画素で水平線形補間して塗りつぶす"""
    L = arr[y0:y1, x0 - 2:x0 - 1].astype(float)
    R = arr[y0:y1, x1 + 1:x1 + 2].astype(float)
    n = x1 - x0
    t = np.linspace(0, 1, n).reshape(1, n, 1)
    arr[y0:y1, x0:x1] = (L * (1 - t) + R * t)
    return arr


def inpaint_v(arr, x0, y0, x1, y1):
    T = arr[y0 - 2:y0 - 1, x0:x1].astype(float)
    B = arr[y1 + 1:y1 + 2, x0:x1].astype(float)
    n = y1 - y0
    t = np.linspace(0, 1, n).reshape(n, 1, 1)
    arr[y0:y1, x0:x1] = (T * (1 - t) + B * t)
    return arr


# ---------------------------------------------------------------- 版面データ
SECTIONS = [
    dict(key='s1', title='ピル・避妊', bar=(644, 702), color='#e35c81', bar_color='#ee7b98',
         rows=['r1']),
    dict(key='s2', title='生理・ホルモン系の悩み', bar=(1001, 1062), color='#92569e', bar_color='#bd86c0',
         rows=['r2', 'r3']),
    dict(key='s3', title='おりもの・外陰部トラブル', bar=(1532, 1592), color='#3d7548', bar_color='#69a371',
         rows=['r4']),
    dict(key='s4', title='性感染症（STD）', bar=(1857, 1914), color='#4e509a', bar_color='#8680bc',
         rows=['r5', 'r6']),
    dict(key='s5', title='妊娠・中絶', bar=(2269, 2326), color='#df5f52', bar_color='#ef9283',
         rows=['r7']),
    dict(key='s6', title='検診・健康チェック', bar=(2502, 2561), color='#50825c', bar_color='#72a27c',
         rows=['r8']),
    dict(key='s7', title='その他の症状・疾患', bar=(2748, 2806), color='#d77c43', bar_color='#e7ae81',
         rows=['r9']),
]
# 見出しテキストの実測インク範囲 (x0,x1,y0,y1)
TITLE_INK = {
    's1': (117, 339, 654, 694), 's2': (114, 625, 1013, 1053), 's3': (114, 638, 1544, 1584),
    's4': (112, 457, 1865, 1907), 's5': (112, 342, 2279, 2320), 's6': (112, 515, 2512, 2552),
    's7': (112, 519, 2757, 2798),
}

ROWS = [
    dict(id='r1', top=732, bot=920, border='#f8dde2',
         cards=[(99, 419), (452, 769), (801, 1121), (1156, 1475), (1510, 1824)],
         labels=['超低用量ピル', '低用量ピル', 'ミニピル', 'アフターピル', 'ミレーナ']),
    dict(id='r2', top=1085, bot=1255, border='#eddced',
         cards=[(98, 417), (452, 767), (801, 1119), (1155, 1471), (1510, 1821)],
         labels=['生理不順', '生理痛', 'PMS（月経前症候群）', '生理がこない（無月経）', '不正出血']),
    dict(id='r3', top=1278, bot=1457, border='#eddced',
         cards=[(98, 418), (452, 767), (801, 1119)],
         labels=['視床下部性無月経', '多のう胞性卵巣\n（PCOS）', '子宮内膜症']),
    dict(id='r4', top=1612, bot=1784, border='#e2ece3',
         cards=[(98, 416), (452, 767), (801, 1119), (1154, 1471), (1510, 1821)],
         labels=['おりものの異常', '外陰部のかゆみ', 'カンジダ膣炎', '細菌性膣症', 'バルトリン腺嚢腫']),
    dict(id='r5', top=1932, bot=2063, border='#e6e4f1',
         cards=[(97, 413), (443, 763), (794, 1106), (1135, 1464), (1496, 1819)],
         labels=['クラミジア', '淋病', '梅毒', 'HIV', '性器ヘルペス']),
    dict(id='r6', top=2078, bot=2210, border='#e6e4f1',
         cards=[(96, 413), (443, 763), (793, 1105), (1135, 1465), (1495, 1819)],
         labels=['コンジローマ', 'ウレアプラズマ', 'マイコプラズマ', 'B型肝炎', 'C型肝炎']),
    dict(id='r7', top=2344, bot=2444, border='#fbe3e0',
         cards=[(98, 405), (444, 763)],
         labels=['妊娠', '人工妊娠中絶']),
    dict(id='r8', top=2578, bot=2694, border='#e5efe7',
         cards=[(98, 485), (520, 911), (953, 1345), (1383, 1770)],
         labels=['婦人科検診', '子宮頸がん検診', 'HPVワクチン', 'ブライダルチェック']),
    dict(id='r9', top=2818, bot=2934, border='#fae7d9',
         cards=[(98, 451), (494, 857), (898, 1272)],
         labels=['膀胱炎', '子宮筋腫', '卵巣嚢腫']),
]

DIVIDERS = [  # (中心y, 色)
    (966, '#fbdade'), (1497, '#e6ebe4'), (1822, '#e4e3f0'),
    (2243, '#fbe4e4'), (2473, '#e4e8e3'), (2722, '#faebe4'),
]

# --------------------------------------------------- 塗りアイコン（2枚目のカンプ）
# IMG_4687.JPG から実測した各アイコンの外接矩形（x, y, w, h）。順序は ROWS のラベルと一致
ICON_SRC = '/Users/hirano/Downloads/IMG_4687.JPG'
ICON_SCALE = 1.860          # 2枚目カンプ→この版面 の倍率（カード間ピッチ実測より）
ICON_BOXES = [
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
# 行ごとのカード地色（2枚目カンプ実測）
CARD_FILL = ['#fdf9f8', '#fcf7fb', '#fcf7fb', '#fbfbf6', '#faf9fe', '#faf9fe',
             '#fdf8f2', '#f4f8f6', '#fcf8f4']

_icon_im = Image.open(ICON_SRC).convert('RGB')
_IA = np.asarray(_icon_im).astype(float)


def extract_icon_color(box, name):
    """カード地色を背景としてアルファを起こし、RGBA で切り出す"""
    x, y, w, h = box
    pad = 5
    crop = _IA[y - pad:y + h + pad, x - pad:x + w + pad].copy()
    # 地色はアイコンの左右（カード内側）から採る
    # 地色はアイコン上辺と左側から採り、文字を拾わないよう明るい画素だけの中央値にする
    ring = [_IA[yy, xx] for yy in range(max(0, y - 14), max(1, y - 7))
            for xx in range(x - 6, x + w + 6) if 0 <= xx < _IA.shape[1]]
    ring += [_IA[yy, x + dx] for yy in range(y, y + h)
             for dx in (-20, -16) if 0 <= x + dx < _IA.shape[1]]
    ring = np.array(ring)
    light = ring[ring.mean(axis=1) > 200]
    BG = np.median(light if len(light) > 20 else ring, axis=0)
    alpha = 1.0 - (crop / np.maximum(BG, 1)).min(axis=2)
    # 地色推定の誤差でうっすら四角が残るのを防ぐ
    alpha = np.clip((alpha - 0.10) / 0.90, 0, 1)
    a3 = np.maximum(alpha, 1e-6)[:, :, None]
    C = np.clip((crop - BG * (1 - a3)) / a3, 0, 255)
    rgba = np.zeros(crop.shape[:2] + (4,), np.uint8)
    rgba[:, :, :3] = C.round().astype(np.uint8)
    rgba[:, :, 3] = (alpha * 255).round().astype(np.uint8)
    p = save_png(rgba, name)
    return dict(src=p, w=crop.shape[1], h=crop.shape[0])


# ---------------------------------------------------------------- アイコン抽出
def extract_icon(x0, y0, x1, y1, name):
    pad = 3
    crop = A[y0 - pad:y1 + 1 + pad, x0 - pad:x1 + 1 + pad].copy()
    flat = crop.reshape(-1, 3)
    d = np.abs(flat - PAGE_BG).sum(axis=1)
    idx = np.argsort(d)[-max(20, len(d) // 60):]
    C = np.median(flat[idx], axis=0)
    denom = PAGE_BG - C
    use = np.abs(denom) > 22
    if not use.any():
        use = np.ones(3, bool)
    alpha = ((PAGE_BG - crop)[:, :, use] / denom[use]).mean(axis=2)
    alpha = np.clip(alpha, 0, 1)
    rgba = np.zeros(crop.shape[:2] + (4,), np.uint8)
    rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2] = [int(round(v)) for v in C]
    rgba[:, :, 3] = (alpha * 255).round().astype(np.uint8)
    p = save_png(rgba, name)
    return dict(src=p, x=x0 - pad, y=y0 - pad, w=crop.shape[1], h=crop.shape[0])


def card_parts(t, b, x0, x1):
    """カード内のアイコン(彩度あり)と文字(無彩色)のインク範囲を実測"""
    ins = 12
    reg = A[t + ins:b - ins, x0 + ins:x1 - ins]
    mx, mn = reg.max(axis=2), reg.min(axis=2)
    sat = mx - mn
    tot = reg.sum(axis=2)
    icon = (sat > 26) & (tot < 735) & (tot > 400)

    def bbox(m, ox, oy):
        ys = np.where(m.any(axis=1))[0]
        xs = np.where(m.any(axis=0))[0]
        if len(ys) == 0:
            return None
        return (ox + xs[0], oy + ys[0], ox + xs[-1], oy + ys[-1])

    ib = bbox(icon, x0 + ins, t + ins)
    # アイコンが左寄り＝横並びレイアウト、中央＝縦並び
    cx = (x0 + x1) / 2
    horiz = abs((ib[0] + ib[2]) / 2 - cx) > 30
    if horiz:
        tx0, ty0 = ib[2] + 8, t + ins
    else:
        tx0, ty0 = x0 + ins, ib[3] + 8
    treg = A[ty0:b - ins, tx0:x1 - ins]
    tot2 = treg.sum(axis=2)
    sat2 = treg.max(axis=2) - treg.min(axis=2)
    text = (sat2 <= 40) & (tot2 < 640)
    tb = bbox(text, tx0, ty0)
    lines = [(ty0 + s, ty0 + e) for s, e in runs(text.any(axis=1), 4)]
    return ib, tb, lines, horiz


# ---------------------------------------------------------------- 実行
parts_html = []
icons_meta = []

for ri, r in enumerate(ROWS):
    t, b = r['top'], r['bot']
    r['icons'], r['label_pos'] = [], []
    for i, (x0, x1) in enumerate(r['cards']):
        ib, tb, lines, horiz = card_parts(t, b, x0, x1)
        r['label_pos'].append(dict(cx=(tb[0] + tb[2]) / 2, cy=(tb[1] + tb[3]) / 2,
                                   h=tb[3] - tb[1], w=tb[2] - tb[0], lines=lines))
        # 塗りアイコンを、元の線アイコンがあった余白に収める
        nb = ICON_BOXES[ri][i]
        meta = extract_icon_color(nb, 'ic_%s_%d.png' % (r['id'], i))
        aspect = meta['w'] / meta['h']
        if horiz:                       # アイコン左・ラベル右のカード
            hh = min(meta['h'] * ICON_SCALE, (b - t) * 0.78)
            cx, cy = (ib[0] + ib[2]) / 2, (ib[1] + ib[3]) / 2
        else:                           # アイコン上・ラベル下のカード
            space = tb[1] - t           # カード上端からラベル上端まで
            hh = min(meta['h'] * ICON_SCALE, space * 0.90)
            cx, cy = (x0 + x1) / 2, t + space / 2
        ww = hh * aspect
        r['icons'].append(dict(src=meta['src'], x=cx - ww / 2, y=cy - hh / 2, w=ww, h=hh))

# ヘッダー（文字をインペイントして背景画に）
hero = A[0:540, :, :].copy()
inpaint_h(hero, 795, 60, 1128, 270)      # Gynecology + 婦人科
inpaint_v(hero, 452, 282, 1468, 336)     # リード文
hero_img = Image.fromarray(np.clip(hero, 0, 255).astype(np.uint8))
hero_p = save_jpg(hero_img, 'hero.jpg', 94)

# 下部セクション背景（カードごと切り出し。カードはこの上に描く）
bot_bg = Image.fromarray(np.clip(A[2950:3563, :, :], 0, 255).astype(np.uint8))
bot_p = save_jpg(bot_bg, 'bottom-bg.jpg', 92)

# 下部カード：帯（見出し文字をインペイント）＋写真
BCARDS = [
    dict(x0=96, x1=925, top=3089, bot=3519,
         title='中絶手術について', t_ink=(186, 3134, 563, 3174),
         photo=(152, 3240, 382, 3487), text_x=431, text_y0=3263, sakura=(824, 3423, 911, 3498),
         body=['母体保護法指定医による安全な', '手術。痛みに配慮した麻酔を使用。',
               '安心して手術を受けていただける', 'よう、丁寧なサポートを心がけて', 'います。']),
    dict(x0=992, x1=1820, top=3089, bot=3519,
         title='ピル処方について', t_ink=(1086, 3134, 1456, 3174),
         photo=(1044, 3240, 1270, 3487), text_x=1316, text_y0=3265, sakura=(1701, 3420, 1796, 3498),
         body=['低用量ピル、緊急避妊用ピル、', '月経困難症治療薬などのピルを',
               '取り扱っています。', '医師が適切なものを提案します。']),
]
for n, bc in enumerate(BCARDS):
    bx0, bx1, btop = bc['x0'], bc['x1'], bc['top']
    band = A[btop:3252, bx0:bx1 + 1].copy()
    tx0, ty0, tx1, ty1 = bc['t_ink']
    inpaint_v(band, tx0 - bx0 - 12, ty0 - btop - 12, tx1 - bx0 + 12, ty1 - btop + 12)
    bc['band_src'] = save_jpg(Image.fromarray(np.clip(band, 0, 255).astype(np.uint8)),
                              'band%d.jpg' % n, 94)
    bc['band_h'] = 3252 - btop
    px0, py0, px1, py1 = bc['photo']
    bc['photo_src'] = save_jpg(im.crop((px0, py0, px1 + 1, py1 + 1)), 'photo%d.jpg' % n, 94)
    # カード上に重なる桜（白背景から抜いてRGBA化）
    sx0, sy0, sx1, sy1 = bc['sakura']
    crop = A[sy0:sy1 + 1, sx0:sx1 + 1]
    alpha = 1.0 - crop.min(axis=2) / 255.0
    a3 = np.maximum(alpha, 1e-6)[:, :, None]
    C = np.clip((crop - 255.0 * (1 - a3)) / a3, 0, 255)
    rgba = np.zeros(crop.shape[:2] + (4,), np.uint8)
    rgba[:, :, :3] = C.round().astype(np.uint8)
    rgba[:, :, 3] = (alpha * 255).round().astype(np.uint8)
    bc['sakura_src'] = save_png(rgba, 'sakura%d.png' % n)

# ---------------------------------------------------------------- HTML 生成
def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;')


html = []
ad = html.append

# ヘッダー
ad('<img class="a hero" src="{{hero}}" style="left:0;top:0;width:1920px;height:540px">')
ad('<div class="a hd-en" style="left:960px;top:99px">Gynecology</div>')
ad('<div class="a hd-ja" style="left:960px;top:205px">婦人科</div>')
ad('<div class="a hd-lead" style="left:960px;top:308px">女性のライフステージごとの体調変化やお悩みに対応いたします</div>')

# セクション
for s in SECTIONS:
    bt, bb = s['bar']
    ad('<div class="a bar" style="left:69px;top:%dpx;height:%dpx;background:%s"></div>'
       % (bt, bb - bt + 1, s['bar_color']))
    ix0, ix1, iy0, iy1 = TITLE_INK[s['key']]
    ad('<div class="a sec-title" style="left:%.1fpx;top:%.1fpx;color:%s">%s</div>'
       % ((ix0 + ix1) / 2, (iy0 + iy1) / 2, s['color'], esc(s['title'])))

# カード
for r in ROWS:
    t, b = r['top'], r['bot']
    for i, (x0, x1) in enumerate(r['cards']):
        ad('<div class="a card" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx;'
           'border-color:%s;background:%s"></div>'
           % (x0, t, x1 - x0 + 1, b - t + 1, r['border'], CARD_FILL[ROWS.index(r)]))
        ic = r['icons'][i]
        ad('<img class="a" src="{{%s}}" style="left:%.1fpx;top:%.1fpx;width:%.1fpx;height:%.1fpx">'
           % (ic['src'], ic['x'], ic['y'], ic['w'], ic['h']))
        lp = r['label_pos'][i]
        label = r['labels'][i]
        if '\n' in label:
            lines = label.split('\n')
            pitch = lp['lines'][-1][0] - lp['lines'][0][0] if len(lp['lines']) > 1 else 40
            ad('<div class="a label ml" style="left:%.1fpx;top:%.1fpx;line-height:%dpx">%s</div>'
               % (lp['cx'], lp['cy'], pitch, '<br>'.join(esc(x) for x in lines)))
        else:
            ad('<div class="a label" style="left:%.1fpx;top:%.1fpx">%s</div>'
               % (lp['cx'], lp['cy'], esc(label)))

# 区切り線
for y, c in DIVIDERS:
    ad('<div class="a hr" style="left:47px;top:%dpx;--dc:%s"></div>' % (y - 1, c))

# 下部
ad('<img class="a" src="{{%s}}" style="left:0;top:2950px;width:1920px;height:613px">' % bot_p)
for bc in BCARDS:
    w = bc['x1'] - bc['x0'] + 1
    h = bc['bot'] - bc['top'] + 1
    ad('<div class="a bcard" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">' % (bc['x0'], bc['top'], w, h))
    ad('  <img class="a" src="{{%s}}" style="left:0;top:0;width:%dpx;height:%dpx">' % (bc['band_src'], w, bc['band_h']))
    tx0, ty0, tx1, ty1 = bc['t_ink']
    ad('  <div class="a band-title" style="left:%.1fpx;top:%.1fpx">%s</div>'
       % ((tx0 + tx1) / 2 - bc['x0'], (ty0 + ty1) / 2 - bc['top'], esc(bc['title'])))
    px0, py0, px1, py1 = bc['photo']
    ad('  <img class="a photo" src="{{%s}}" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">'
       % (bc['photo_src'], px0 - bc['x0'], py0 - bc['top'], px1 - px0 + 1, py1 - py0 + 1))
    ad('  <div class="a body" style="left:%dpx;top:%dpx">%s</div>'
       % (bc['text_x'] - bc['x0'] - 3, bc['text_y0'] - bc['top'] - 11, '<br>'.join(esc(x) for x in bc['body'])))
    sx0, sy0, sx1, sy1 = bc['sakura']
    ad('  <img class="a" src="{{%s}}" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">'
       % (bc['sakura_src'], sx0 - bc['x0'], sy0 - bc['top'], sx1 - sx0 + 1, sy1 - sy0 + 1))
    ad('</div>')

# ---------------------------------------------------------------- アクセス・診療時間
# 出典: https://sakura-ikebukuro.com/ （2026-08-05 取得）／地図の埋め込みコードは施主支給
MAP_SRC = ('https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3241.5!'
           '2d139.69699527738007!3d35.68912741970208!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!'
           '4f13.1!3m3!1m2!1s0x60188dec4a4e4c6b%3A0x3d7c4fc94b0f591b!'
           '2z5rGg6KKL6aeF5YmN44GV44GP44KJ44Os44OH44Kj44O844K544Kv44Oq44OL44OD44KvTklDT'
           '-ODrOODh-OCo-ODvOOCueearuOBteenkQ!5e0!3m2!1sja!2sjp!4v1785900964372!5m2!1sja!2sjp')
CLINIC = dict(
    name='池袋駅前さくらレディースクリニック<br>NICOレディース皮ふ科',
    addr='〒170-0013<br>東京都豊島区東池袋1丁目1-4 タカセセントラルビル 4階',
    tel='03-5944-9105',
    access='池袋駅東口から徒歩1分<br>35番出口から徒歩0分',
    hours=[['曜日', '診療時間'],
           ['月曜', '11:00〜14:00 ／ 15:00〜21:00'],
           ['火曜', '11:00〜17:00 ／ 17:00〜21:00'],
           ['水曜', '11:00〜15:00 ／ 17:00〜21:00'],
           ['木曜', '11:00〜15:00 ／ 17:00〜21:00'],
           ['金曜', '11:00〜15:00 ／ 17:00〜21:00'],
           ['土・日・祝日', '10:00〜14:00 ／ 15:00〜18:00']],
    notes=['※火曜日は休診時間なく診療しております。', '※いずれの時間帯も女性医師が担当します。'],
)
SEC_TOP = 3660                     # 見出しバーの上端
CX, CW = 96, 1730                  # コンテンツ左端と幅
MAP_Y, MAP_H = 3790, 620
GAP = 70
LCOL_W = 800                       # 左：医院情報
RCOL_X = CX + CW - 830             # 右：診療時間
TITLE = 'アクセス・診療時間'

ad('<div class="a bar" style="left:69px;top:%dpx;height:59px;background:#ee7b98"></div>' % SEC_TOP)
# 他セクションと同じく「文字の中心」を渡す（左端112px 起点）
ad('<div class="a sec-title" style="left:%dpx;top:%dpx;color:#e35c81">%s</div>'
   % (112 + len(TITLE) * 46.3 / 2, SEC_TOP + 30, TITLE))

# 地図（上）
ad('<div class="a acc-map" style="left:%dpx;top:%dpx;width:%dpx;height:%dpx">'
   '<div class="map-fb">Googleマップ（表示にはネットワーク接続が必要です）</div>'
   '<iframe src="%s" title="%s の地図" loading="lazy" allowfullscreen '
   'referrerpolicy="strict-origin-when-cross-origin"></iframe></div>'
   % (CX, MAP_Y, CW, MAP_H, MAP_SRC, '池袋駅前さくらレディースクリニック'))

# 左カラム：医院名＋所在地・電話・アクセス
y = MAP_Y + MAP_H + GAP
ad('<div class="a acc-name" style="left:%dpx;top:%dpx;width:%dpx">%s</div>' % (CX, y, LCOL_W, CLINIC['name']))
y += 112
for label, value, lines in [('所在地', CLINIC['addr'], 2),
                            ('電話番号', '<a href="tel:%s">%s</a>' % (CLINIC['tel'].replace('-', ''), CLINIC['tel']), 1),
                            ('アクセス', CLINIC['access'], 2)]:
    ad('<div class="a acc-rule" style="left:%dpx;top:%dpx;width:%dpx"></div>' % (CX, y, LCOL_W))
    ad('<div class="a acc-label" style="left:%dpx;top:%dpx">%s</div>' % (CX, y + 26, label))
    ad('<div class="a acc-val" style="left:%dpx;top:%dpx;width:%dpx">%s</div>' % (CX, y + 66, LCOL_W, value))
    y += 66 + 43 * lines + 34
ad('<div class="a acc-rule" style="left:%dpx;top:%dpx;width:%dpx"></div>' % (CX, y, LCOL_W))
LEFT_BOTTOM = y

# 右カラム：診療時間
ty = MAP_Y + MAP_H + GAP
rows = ''.join('<tr>%s</tr>' % ''.join(
    '<%s>%s</%s>' % ('th' if (ri == 0 or ci == 0) else 'td', esc(c), 'th' if (ri == 0 or ci == 0) else 'td')
    for ci, c in enumerate(r)) for ri, r in enumerate(CLINIC['hours']))
ad('<table class="a hours" style="left:%dpx;top:%dpx;width:830px">%s</table>' % (RCOL_X, ty, rows))
ny = ty + 66 * len(CLINIC['hours']) + 20
for n in CLINIC['notes']:
    ad('<div class="a acc-note" style="left:%dpx;top:%dpx">%s</div>' % (RCOL_X, ny, esc(n)))
    ny += 38

PAGE_H = max(LEFT_BOTTOM, ny) + 96

body = '\n'.join(html)

CSS = """
:root{
  --mincho:"Hiragino Mincho ProN","HiraMinProN-W3","Yu Mincho","YuMincho",serif;
  --gothic:"Hiragino Kaku Gothic ProN","Hiragino Sans","Yu Gothic","YuGothic",sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html{background:#fff}
body{background:#fff;-webkit-font-smoothing:antialiased}
#fit{width:100%;overflow:hidden}
#stage{position:relative;width:1920px;height:__PH__px;background:#fdfafb;
  transform-origin:top left;font-family:var(--gothic);color:#333}
.a{position:absolute}
img.a{display:block;border:0}

/* ヘッダー */
.hd-en{transform:translate(-50%,-50%);font-family:"Times New Roman",var(--mincho),serif;
  font-size:52px;letter-spacing:.055em;color:#d76a7e;text-indent:.055em;white-space:nowrap}
.hd-ja{transform:translate(-50%,-50%);font-family:var(--mincho);font-size:90px;
  letter-spacing:.10em;color:#46241b;text-indent:.10em;white-space:nowrap}
.hd-lead{transform:translate(-50%,-50%);font-size:33px;font-weight:500;-webkit-text-stroke:.25px;letter-spacing:.025em;
  color:#4a3c38;text-indent:.025em;white-space:nowrap}

/* セクション見出し */
.bar{width:11px;border-radius:2px}
.sec-title{transform:translate(-50%,-50%);font-family:var(--mincho);font-size:45px;
  font-weight:400;-webkit-text-stroke:.3px;letter-spacing:.03em;text-indent:.03em;white-space:nowrap;line-height:1}

/* カード */
.card{border:2px solid;border-radius:9px}
.label{transform:translate(-50%,-50%);font-size:26px;font-weight:500;-webkit-text-stroke:.4px;letter-spacing:.05em;
  text-indent:.05em;white-space:nowrap;line-height:1;color:#454343}
.label.ml{text-align:center}

/* 区切り線 */
.hr{width:1817px;height:3px;
  background:repeating-linear-gradient(to right,var(--dc) 0 8px,transparent 8px 13.6px)}

/* 下部カード */
.bcard{background:#fff;border:2px solid #f8dbe4;border-radius:14px;overflow:hidden}
.band-title{transform:translate(-50%,-50%);font-family:var(--mincho);font-size:46px;
  letter-spacing:.04em;text-indent:.04em;color:#fff;white-space:nowrap;line-height:1}
.photo{border-radius:4px;object-fit:cover}
.body{font-size:27px;line-height:43.7px;letter-spacing:.04em;color:#3f3532;-webkit-text-stroke:.3px}

/* アクセス・診療時間 */
.acc-map{border:2px solid #f0dbe1;border-radius:9px;overflow:hidden;background:#f4f1ee}
.acc-map iframe{position:relative;z-index:1;width:100%;height:100%;border:0;display:block}
.map-fb{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
  font-size:24px;letter-spacing:.04em;color:#9c8f8b;text-align:center;padding:0 40px}
.acc-name{font-family:var(--mincho);font-size:38px;letter-spacing:.05em;color:#3b2118;line-height:1.42}
.acc-rule{height:1px;background:#ecdfe3}
.acc-label{font-size:23px;font-weight:600;letter-spacing:.14em;color:#c4738c;line-height:1}
.acc-val{font-size:28px;line-height:43px;letter-spacing:.04em;color:#3f3532}
.acc-val a{color:#3f3532;text-decoration:none;border-bottom:1px solid #e6ccd4}
.acc-val a:hover{color:#d4557a}
.hours{border-collapse:collapse;font-size:26px;letter-spacing:.04em;
  font-variant-numeric:tabular-nums;color:#3f3532}
.hours th,.hours td{border:1px solid #eddfe3;height:66px;text-align:center;font-weight:400}
.hours tr:first-child th{background:#fdf1f4;color:#c04c72;font-weight:600;letter-spacing:.1em}
.hours tr:not(:first-child) th{background:#fbf7f8;width:230px}
.acc-note{font-size:24px;letter-spacing:.04em;color:#6b5f5c;line-height:1}
"""

doc = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>婦人科ページ カンプ再現</title>
<style>%s</style>
</head>
<body>
<div id="fit"><div id="stage">
%s
</div></div>
<script>
(function(){
  var fit=document.getElementById('fit'), st=document.getElementById('stage');
  function r(){var s=fit.clientWidth/1920; st.style.transform='scale('+s+')';
    fit.style.height=Math.round(__PH__*s)+'px';}
  r(); addEventListener('resize',r);
})();
</script>
</body>
</html>
""" % (CSS, body)

# 画像を base64 に差し替え
cache = {}
for p in set(list(icons_meta) + [hero_p, bot_p] +
             [b['band_src'] for b in BCARDS] + [b['photo_src'] for b in BCARDS] +
             [b['sakura_src'] for b in BCARDS] +
             [ic['src'] for r in ROWS for ic in r['icons']]):
    cache[p] = b64(p)
doc = doc.replace('__PH__', str(PAGE_H))
doc = doc.replace('{{hero}}', cache[hero_p])
for p, d in cache.items():
    doc = doc.replace('{{%s}}' % p, d)

out = os.path.join(OUT_DIR, 'index.html')
with open(out, 'w') as f:
    f.write(doc)
print('written', out, '%.1f KB' % (len(doc) / 1024))
