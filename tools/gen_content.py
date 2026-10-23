#!/usr/bin/env python3
# 从博客手册生成 content.js（战术手册/训练手册），保持网站与文章同源。
# 用法：python3 tools/gen_content.py   （文章更新后重跑 → git push 即上线）
import re, html, json, os

MD = '/Users/luxiaopeng/github/blog/source/_posts/war3-website.md'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'content.js')

lines = open(MD).read().split('\n')

def locate(prefix):
    for i, l in enumerate(lines):
        if l.startswith(prefix):
            return i
    raise SystemExit('heading not found: ' + prefix)

def section(prefix):
    s = locate(prefix)
    lvl = len(prefix) - len(prefix.lstrip('#'))
    e = len(lines)
    for j in range(s + 1, len(lines)):
        m = re.match(r'^(#{2,6})[^#]', lines[j])
        if m and len(m.group(1)) <= lvl:
            e = j
            break
    return lines[s:e]

def strip_num(s):
    return re.sub(r'^(\d+\.\d+\s+|[一二三四五六七八九十]+、\s*)', '', s).strip()

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',
               lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
               lambda m: f'<a href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    return t

HERE = os.path.dirname(os.path.abspath(__file__))

def localize(h):
    # 博客图床 URL → 站点本地资源（有本地副本的）
    for name in os.listdir(os.path.join(HERE, '..', 'assets', 'war3')):
        h = h.replace('https://lucifer.ren/blog/images/war3/' + name, 'assets/war3/' + name)
    return h

def to_html(ls):
    out = []
    i, n = 0, len(ls)
    def flush(buf, typ):
        if not buf:
            return
        if typ == 'ol':
            start = buf[0][0]
            body = ''.join(f'<li>{x}</li>' for _, x in buf)
            out.append(f'<ol start="{start}">{body}</ol>')
        else:
            out.append('<ul>' + ''.join(f'<li{x}>{y}</li>' for x, y in buf) + '</ul>')
        buf.clear()
    ul, ol = [], []
    while i < n:
        l = lines[i] if False else ls[i]
        if l.startswith('```'):
            flush(ul, 'ul'); flush(ol, 'ol')
            j = i + 1; buf = []
            while j < n and not ls[j].startswith('```'):
                buf.append(ls[j]); j += 1
            out.append('<pre><code>' + html.escape('\n'.join(buf)) + '</code></pre>')
            i = j + 1; continue
        if l.startswith('|'):
            flush(ul, 'ul'); flush(ol, 'ol')
            j = i; rows = []
            while j < n and ls[j].startswith('|'):
                cells = [c.strip() for c in ls[j].strip().strip('|').split('|')]
                if not re.match(r'^:?-+:?$', cells[0] if cells else '--'):
                    rows.append(cells)
                j += 1
            if rows:
                t = '<table>'
                head, body = (rows[0], rows[1:]) if len(rows) > 1 else (None, rows)
                if head:
                    t += '<tr>' + ''.join(f'<th>{inline(c)}</th>' for c in head) + '</tr>'
                for r in body:
                    t += '<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>'
                out.append(t + '</table>')
            i = j; continue
        m = re.match(r'^(\s*)- (.*)', l)
        if m:
            flush(ol, 'ol')
            cls = ' class="sub"' if len(m.group(1)) >= 2 else ''
            ul.append((cls, inline(m.group(2))))
            i += 1; continue
        m = re.match(r'^\s*(\d+)\. (.*)', l)
        if m:
            flush(ul, 'ul')
            ol.append((int(m.group(1)), inline(m.group(2))))
            i += 1; continue
        if l.startswith('>'):
            flush(ul, 'ul'); flush(ol, 'ol')
            out.append('<blockquote>' + inline(l.lstrip('> ').strip()) + '</blockquote>')
            i += 1; continue
        if l.startswith('#'):
            flush(ul, 'ul'); flush(ol, 'ol')
            h = len(l) - len(l.lstrip('#'))
            out.append(f'<h{h}>{inline(strip_num(l.lstrip("#").strip()))}</h{h}>')
            i += 1; continue
        if not l.strip():
            flush(ul, 'ul'); flush(ol, 'ol')
            i += 1; continue
        flush(ul, 'ul'); flush(ol, 'ol')
        out.append('<p>' + inline(l.strip()) + '</p>')
        i += 1
    flush(ul, 'ul'); flush(ol, 'ol')
    return localize('\n'.join(out))

TACTIC = ['### 4.1', '### 4.2', '### 4.3', '### 4.4', '### 4.5', '### 4.6']
MICRO_ARTICLE = ['## 六、微操：让 APM 花在刀刃上']
MICRO_PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pages', 'micro.md')

def build(prefixes):
    res = []
    for p in prefixes:
        ls = section(p)
        title = ls[0].lstrip('#').strip()
        frag = {'id': re.sub(r'[^0-9A-Za-z]', '', p)[:10], 'title': strip_num(title),
                'html': to_html(ls[1:])}
        res.append(frag)
    return res

def subfrags(prefix, race):
    # 把 ### 4.x 按 #### 拆成战术片段；#### 之前的内容作为「总则与开局」
    ls = section(prefix)
    idxs = [i for i, l in enumerate(ls) if l.startswith('#### ')]
    res = []
    if not idxs:
        return [{'id': f'{race}-0', 'title': ls[0].lstrip('#').strip(), 'html': to_html(ls[1:])}]
    intro = ls[1:idxs[0]]
    if any(l.strip() for l in intro):
        res.append({'id': f'{race}-0', 'title': '总则与开局', 'html': to_html(intro)})
    for k, i in enumerate(idxs):
        end = idxs[k + 1] if k + 1 < len(idxs) else len(ls)
        res.append({'id': f'{race}-{k+1}', 'title': strip_num(ls[i].lstrip('#').strip()),
                    'html': to_html(ls[i + 1:end])})
    return res

micro = build(MICRO_ARTICLE)
mlines = open(MICRO_PAGE).read().split('\n')
micro.append({'id': 'ref', 'title': strip_num(mlines[0].lstrip('#').strip()), 'html': to_html(mlines[1:])})
t41 = build(['### 4.1'])[0]
t46 = build(['### 4.6'])[0]
content = {
    'tactic': {
        'common': [t41, t46],
        'orc': subfrags('### 4.2', 'orc'),
        'ne': subfrags('### 4.3', 'ne'),
        'hum': subfrags('### 4.4', 'hum'),
        'ud': subfrags('### 4.5', 'ud'),
    },
    'micro': micro,
}
with open(OUT, 'w') as f:
    f.write('const CONTENT=')
    json.dump(content, f, ensure_ascii=False)
print('micro:', [(x['title'], len(x['html'])) for x in content['micro']])
print('tactic races:', {r:[f['title'] for f in fs] for r,fs in content['tactic'].items()})
