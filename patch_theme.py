# -*- coding: utf-8 -*-
"""本番テーマ page/gynecology.php を書き換える。
   ・診療一覧のタグ羅列 → アイコンカード
   ・アクセス・診療時間セクションを追加
   ・専用CSSの読み込みを追加
   元ファイルは gynecology.php20260805 として退避する。"""
import re, os, shutil

THEME = '/Users/hirano/Downloads/sakuratheme'
PHP = os.path.join(THEME, 'page/gynecology.php')

# カテゴリ順（既存PHPの並びと一致）／(ラベル, アイコン番号)
CATS = [
    ['超低用量ピル', '低用量ピル', 'ミニピル', 'アフターピル', 'ミレーナ'],
    ['生理不順', '生理痛', 'PMS（月経前症候群）', '生理がこない（無月経）', '不正出血',
     '視床下部性無月経', '多のう胞性卵巣（PCOS）', '子宮内膜症'],
    ['おりものの異常', '外陰部のかゆみ', 'カンジダ膣炎', '細菌性膣症', 'バルトリン腺嚢腫'],
    ['クラミジア', '淋病', '梅毒', 'HIV', '性器ヘルペス',
     'コンジローマ', 'ウレアプラズマ', 'マイコプラズマ', 'B型肝炎', 'C型肝炎'],
    ['妊娠', '人工妊娠中絶'],
    ['婦人科検診', '子宮頸がん検診', 'HPVワクチン', 'ブライダルチェック'],
    ['膀胱炎', '子宮筋腫', '卵巣嚢腫'],
]
WIDE = {4, 5, 6}          # 横並び（アイコン左・文字右）にするカテゴリの index

TPL_URI = "<?= get_template_directory_uri(); ?>"


def cards_markup(items, start, wide, indent='        '):
    cls = 'sec1__cards' + (' sec1__cards--wide' if wide else '')
    out = ['%s<ul class="%s">' % (indent, cls)]
    for i, label in enumerate(items):
        out.append('%s  <li>' % indent)
        out.append('%s    <img src="%s/assets/images/gyne/ico/ic-%02d.png" alt="" width="120" height="120" loading="lazy" decoding="async">'
                   % (indent, TPL_URI, start + i))
        out.append('%s    <span>%s</span>' % (indent, label))
        out.append('%s  </li>' % indent)
    out.append('%s</ul>' % indent)
    return '\n'.join(out)


ACCESS = '''
  <section class="sec sec-access" id="access">
    <div class="inner">
      <div class="sec__title">
        <p class="is-didot">Access</p>
        <h2>アクセス・診療時間</h2>
      </div>

      <div class="gyn-access__map">
        <iframe
          src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3241.5!2d139.69699527738007!3d35.68912741970208!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x60188dec4a4e4c6b%3A0x3d7c4fc94b0f591b!2z5rGg6KKL6aeF5YmN44GV44GP44KJ44Os44OH44Kj44O844K544Kv44Oq44OL44OD44KvTklDT-ODrOODh-OCo-ODvOOCueearuOBteenkQ!5e0!3m2!1sja!2sjp!4v1785900964372!5m2!1sja!2sjp"
          title="池袋駅前さくらレディースクリニックNICOレディース皮ふ科の地図"
          loading="lazy" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>
      </div>

      <div class="gyn-access__body">
        <div class="gyn-access__info">
          <p class="gyn-access__name">池袋駅前さくらレディースクリニック<br>NICOレディース皮ふ科</p>
          <dl>
            <dt>所在地</dt>
            <dd>〒170-0013<br>東京都豊島区東池袋1丁目1-4 タカセセントラルビル4階</dd>
            <dt>電話番号</dt>
            <dd><a href="tel:0359449105" aria-label="03-5944-9105に電話をかける">03-5944-9105</a></dd>
            <dt>アクセス</dt>
            <dd>池袋駅東口から徒歩1分<br>35番出口から徒歩0分</dd>
          </dl>
        </div>

        <div class="gyn-access__hours">
          <table>
            <thead>
              <tr><th>曜日</th><th>診療時間</th></tr>
            </thead>
            <tbody>
              <tr><th>月曜</th><td>11:00〜14:00 ／ 15:00〜21:00</td></tr>
              <tr><th>火曜</th><td>11:00〜17:00 ／ 17:00〜21:00</td></tr>
              <tr><th>水曜</th><td>11:00〜15:00 ／ 17:00〜21:00</td></tr>
              <tr><th>木曜</th><td>11:00〜15:00 ／ 17:00〜21:00</td></tr>
              <tr><th>金曜</th><td>11:00〜15:00 ／ 17:00〜21:00</td></tr>
              <tr><th>土・日・祝日</th><td>10:00〜14:00 ／ 15:00〜18:00</td></tr>
            </tbody>
          </table>
          <p class="gyn-access__note">※火曜日は休診時間なく診療しております。</p>
          <p class="gyn-access__note">※いずれの時間帯も女性医師が担当します。</p>
        </div>
      </div>
    </div>
  </section>
'''

src = open(PHP, encoding='utf-8').read()
bak = PHP + '20260805'
if not os.path.exists(bak):
    shutil.copy2(PHP, bak)

# 1) タグ羅列 → アイコンカード
blocks = re.findall(r'[ \t]*<ul class="sec1__tags">.*?</ul>', src, re.S)
assert len(blocks) == 7, len(blocks)
start = 1
for i, blk in enumerate(blocks):
    src = src.replace(blk, cards_markup(CATS[i], start, i in WIDE), 1)
    start += len(CATS[i])

# 2) 専用CSSの読み込み
old_link = '<link rel="stylesheet" href="<?= get_template_directory_uri(); ?>/assets/css/style_test.css">'
assert old_link in src
src = src.replace(old_link, old_link + '\n' +
                  '<link rel="stylesheet" href="<?= get_template_directory_uri(); ?>/assets/css/gynecology-cards.css">', 1)

# 3) アクセス欄を </main> 直前に
assert src.rstrip().endswith('</main>')
src = src.rstrip()[:-len('</main>')].rstrip() + '\n' + ACCESS + '</main>\n'

open(PHP, 'w', encoding='utf-8').write(src)
print('patched:', PHP)
print('backup :', bak)
print('cards  :', start - 1, '個')
