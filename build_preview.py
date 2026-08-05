# -*- coding: utf-8 -*-
"""本番HTML(取得済) の <main> を、書き換えたテンプレートの中身に差し替えたプレビューを作る"""
import re
THEME = '/Users/hirano/Downloads/sakuratheme'
live = open('/private/tmp/claude-501/-Users-hirano/359a154a-2db5-441c-8f25-00c2244f40e0/scratchpad/live_gyn.html', encoding='utf-8').read()
php  = open(THEME + '/page/gynecology.php', encoding='utf-8').read()
# PHPのテンプレートURI出力をローカル相対パスに
php = re.sub(r"<\?=\s*get_template_directory_uri\(\);\s*\?>", ".", php)
php = re.sub(r"<\?.*?\?>", "", php, flags=re.S)
main_new = re.search(r'<main.*?</main>', php, re.S).group(0)
css_links = re.findall(r'<link rel="stylesheet"[^>]*>', php)
out = re.sub(r'<main.*?</main>', lambda m: main_new, live, flags=re.S)
links = '\n'.join(css_links)
out = out.replace('</head>', links + '\n</head>', 1)
# 追加CSSをheadに（テンプレ側のlinkはmain内にあるのでそのまま効く）
open(THEME + '/_preview.html', 'w', encoding='utf-8').write(out)
print('preview written', len(out), 'bytes / css links in template:', len(css_links))
