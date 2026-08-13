#!/usr/bin/env python3
"""Generate apps.alisher.xyz/index.html.

Frontend adopted from vpavlin's apps.vpavlin.xyz (his exact chrome — header, tabs,
"How to install" blocks, footer, card layout, theme toggle), populated with OUR content:
  · Basecamp tab  — our catalog modules, with a collapsible
                    "Not currently maintained on Basecamp" group (github + untested).
  · Android tab   — our F-Droid apps: Peers, Booth, Receiver.
Icons are embedded as data: URIs; the page is fully self-contained.
"""
import base64, glob, os, html, io, json, subprocess, tempfile
from PIL import Image

GH = "https://github.com/xAlisher"
REPO_JSON = "https://apps.alisher.xyz/logos-repo.json"
FDROID_REPO = "https://xalisher.github.io/fdroid/repo"
FDROID_FP = "9283C4E3DAB31E68675B643AE38222358541431AD07295B6DF4A4C6D2ACCCF32"
BASE = os.path.expanduser('~/basecamp/modules')


# Every icon is normalized to the SAME layout as the Docs reference: the visible
# content is cropped, scaled so its longer side is TARGET_FRAC of the canvas, and
# centered on a transparent square — giving a uniform icon-to-edge margin (~23%).
CANVAS = 256
TARGET_FRAC = 0.54  # Docs reference: content ≈ 54% of canvas → ~23% margin each side


def _load_rgba(p):
    if p.endswith('.svg'):
        tmp = None
        try:
            fd, tmp = tempfile.mkstemp(suffix='.png')   # atomically created — no symlink race
            os.close(fd)
            subprocess.run(['rsvg-convert', '-w', '512', '-h', '512', p, '-o', tmp],
                           check=True, capture_output=True)
            return Image.open(tmp).convert('RGBA')
        except Exception:
            return None
        finally:
            if tmp:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
    return Image.open(p).convert('RGBA')


def normalize_uri(src_path):
    """Crop to content, scale longer side to TARGET_FRAC of the canvas, center on transparent."""
    im = _load_rgba(src_path)
    if im is None:
        return None
    bb = im.split()[-1].getbbox()
    if bb:
        im = im.crop(bb)
    cw, ch = im.size
    scale = (CANVAS * TARGET_FRAC) / max(cw, ch)
    nw, nh = max(1, round(cw * scale)), max(1, round(ch * scale))
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new('RGBA', (CANVAS, CANVAS), (0, 0, 0, 0))
    canvas.paste(im, ((CANVAS - nw) // 2, (CANVAS - nh) // 2), im)
    buf = io.BytesIO()
    canvas.save(buf, 'PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def resolve_icon_path(m):
    if m.get('iconpath') and os.path.exists(m['iconpath']):
        return m['iconpath']
    d = m.get('mdir') or f'{BASE}/{m["repo"]}'
    cands = []
    if m.get('icon'):
        cands += glob.glob(f'{d}/{m["icon"]}') + glob.glob(f'{d}/**/{m["icon"]}', recursive=True)
    cands += glob.glob(f'{d}/**/*.png', recursive=True) + glob.glob(f'{d}/**/*.svg', recursive=True)
    for p in cands:
        low = p.lower()
        if any(x in low for x in ('demo', 'screenshot', 'listener', 'host-stream', 'social', 'sidebar', 'preview')):
            continue
        if os.path.getsize(p) > 300_000:
            continue
        return p
    return None


def module_icon(m):
    p = resolve_icon_path(m)
    return normalize_uri(p) if p else None


def read_meta(m):
    """Real (name, version, dependencies) from the primary module's metadata.json — no curation."""
    mdir = m.get('mdir') or f'{BASE}/{m["repo"]}'
    prim = m['primary']
    best = None  # (path-depth, version, deps) — prefer the canonical (shallowest) manifest
    for f in glob.glob(f'{mdir}/**/metadata.json', recursive=True):
        try:
            j = json.load(open(f))
        except Exception:
            continue
        if j.get('name') == prim:
            depth = f.count(os.sep)
            if best is None or depth < best[0]:
                best = (depth, j.get('version'), j.get('dependencies') or j.get('requires') or [])
    if best:
        return best[1], best[2]
    return None, []


# ── Basecamp catalog modules (bucket: catalog | github | untested) ──
# `primary` = the canonical module (its real name, version and dependencies are read
# from that module's metadata.json — no curation). `mdir` overrides the checkout dir.
A = [
 # in this repository (catalog, tested on 0.2.x)
 dict(bucket='catalog', repo='docs-logos', title='Docs', primary='docs_logos', cat='Utility', icon='',
      mdir=os.path.expanduser('~/docs-assistant'),
      iconpath=os.path.expanduser('~/docs-assistant/qml/icon.png'),
      desc='Search the Basecamp & Logos docs and blog inside Basecamp — on-device keyword search with a full-screen Markdown reader. Linux + macOS.'),
 dict(bucket='catalog', repo='logos-blockchain-ui', title='Blockchain node', primary='logos_node_1click', cat='Blockchain', icon='',
      desc='Community 1-click fork — run a Logos testnet node in one click. Live Blend status, a durable proposals tab and a node settings modal.'),
 dict(bucket='github', repo='ia-basecamp', title='Archive', primary='archive_ui', cat='Archiving', icon='archive.png',
      desc='Follow curated LEZ channels and preserve their Internet Archive collections to Logos Storage.'),
 dict(bucket='catalog', repo='receiver-basecamp', title='Receiver', primary='receiver_ui', cat='Streaming', icon='',
      iconpath=os.path.expanduser('~/basecamp/modules/receiver-basecamp/qml/receiver.png'),
      desc='Discover and listen to decentralized Logos radio broadcasts over the delivery module, via Tor. Bundles its own ffplay + Tor, zero-install (Linux + macOS).'),
 dict(bucket='catalog', repo='booth-basecamp', title='Booth (xRadio)', primary='radio_ui', cat='Streaming', icon='',
      iconpath=os.path.expanduser('~/basecamp/modules/booth-basecamp/radio_ui/icons/radio.png'),
      desc='Broadcast your own decentralized station — RTMP to MediaMTX, announced over the delivery module.'),
 dict(bucket='catalog', repo='lez-stark-verify', title='ZK Guess', primary='zk_guess_game', cat='Game', icon='',
      mdir=os.path.expanduser('~/lez-stark-verify/module/zk-guess-game'),
      iconpath=os.path.expanduser('~/lez-stark-verify/module/zk-guess-game/qml/icon.png'),
      desc='Provably-fair number-guessing game — the machine proves above/below without revealing the number, then settles the win on-zone (STARK-verified).'),
 # also on GitHub (works on 0.2.x, install from source)
 dict(bucket='github', repo='keeper-basecamp', title='Keeper', primary='keeper_ui', cat='Archiving', icon='keeper.png',
      desc='Preserve Internet Archive collections — download, store CIDs on Logos Storage, inscribe on-chain.'),
 dict(bucket='github', repo='beacon-basecamp', title='Beacon', primary='logos_beacon', cat='Blockchain', icon='',
      desc='On-chain CID inscription — sequence content references onto the Logos Execution Zone.'),
 dict(bucket='github', repo='stash-basecamp', title='Stash', primary='stash_ui', cat='Storage', icon='',
      iconpath=os.path.expanduser('~/basecamp/modules/stash-basecamp/plugins/stash_ui/qml/icons/Stash_sidebar.png'),
      desc='Connects decentralised storage (Kubo, Pinata or Logos) to your module.'),
 dict(bucket='github', repo='keycard-basecamp', title='Keycard', primary='keycard-ui', cat='Security', icon='keycard.png',
      desc='Smartcard authentication — unlock and sign with a hardware Keycard.'),
 dict(bucket='github', repo='qr-basecamp', title='QR', primary='qr_ui', cat='Utility', icon='',
      desc='Generate and scan QR codes inside Basecamp — share CIDs, keys and links.'),
 # not tested in Basecamp 0.2.x
 dict(bucket='untested', repo='cord-basecamp', title='Cord', primary='cord_ui', cat='Social', icon='cord.png',
      desc='Social layer — subscribe to Beacon channels and follow on-chain publishers.'),
 dict(bucket='untested', repo='logos-notes', title='Notes', primary='notes_ui', cat='Productivity', icon='',
      iconpath=os.path.expanduser('~/basecamp/modules/logos-notes/plugins/notes_ui/qml/icons/notes.png'),
      desc='Encrypted, local-first notes for the Logos ecosystem.'),
 dict(bucket='untested', repo='logos-wallet-basecamp', title='Wallet', primary='wallet_ui', cat='Finance', icon='',
      desc='Native token wallet — accounts, faucet, and keycard-gated transfers.'),
 dict(bucket='untested', repo='soulseek-basecamp', title='Soulseek', primary='soulseek_ui', cat='Music', icon='',
      desc='Soulseek music search, download, and playlist management.'),
 dict(bucket='untested', repo='scorched-earth-basecamp', title='Scorched Earth', primary='scorched_earth_ui', cat='Game', icon='',
      mdir=os.path.expanduser('~/basecamp/modules/scorched-earth'),
      iconpath=os.path.expanduser('~/basecamp/modules/scorched-earth/scorched-earth-ui/icons/scorched-earth.png'),
      desc='Turn-based artillery game — hot-seat or P2P multiplayer over Waku, no server or accounts.'),
 dict(bucket='untested', repo='logos-snake-game', title='Snake', primary='snake-ui', cat='Game', icon='',
      desc='The classic Snake — a Basecamp mini-game.'),
 dict(bucket='untested', repo='logos-node-basecamp', title='Logos Node', primary='node_ui', cat='Infrastructure', icon='',
      desc='Run and manage a Logos blockchain node from inside Basecamp.'),
]

# ── Android apps (F-Droid repo) ──
ANDROID = [
 dict(title='Node Remote', ver='0.1.0', bytes=28151039, cat='Internet',
      apk='node-remote-0.1.0-arm64.apk',
      iconpath=os.path.expanduser('/home/alisher/basecamp/modules/node-remote/node-remote-bc/node_remote_ui/icons/node-remote.png'),
      desc='Watch and control your Logos blockchain node from your phone, over Tor.'),
 dict(title='Peers', ver='0.9.15', bytes=48728940, cat='Communication',
      apk='peers-0.9.15-arm64.apk',
      iconpath=os.path.expanduser('~/projects/peers-tech-landing/apple-touch-icon.png'),
      desc='Local-first peer-to-peer chat on Logos — encrypted direct messaging over Waku, no server or account.'),
 dict(title='Booth', ver='0.1.0', bytes=49766209, cat='Multimedia',
      apk='booth-android-0.1.0-arm64.apk',
      iconpath=os.path.expanduser('~/basecamp/modules/booth-basecamp/radio_ui/icons/radio.png'),
      desc='Broadcast a decentralized radio station from your phone — announced over Logos delivery.'),
 dict(title='Receiver', ver='1.0.1', bytes=37237746, cat='Multimedia',
      apk='receiver-android-1.0.1-arm64.apk',
      iconpath=os.path.expanduser('~/basecamp/modules/receiver-basecamp/qml/receiver.png'),
      desc='Discover and listen to decentralized Logos radio broadcasts on the go.'),
]


def esc(s):
    return html.escape(s)


def icon_html(uri, letter):
    if uri:
        return f'<img class="icon" src="{uri}" alt="" loading="lazy"/>'
    return f'<div class="icon fallback">{esc(letter)}</div>'


def bc_card(m):
    uri = module_icon(m)
    link = f'{GH}/{m["repo"]}'
    ver, deps = read_meta(m)
    deps_html = ''
    if deps:
        chips = ''.join(f'<span class="dep">{esc(x)}</span>' for x in deps)
        deps_html = f'<div class="deps">needs {chips}</div>'
    vlabel = f' &middot; v{esc(ver)}' if ver else ''
    meta = f'<code class="mod">{esc(m["primary"])}</code>{vlabel}'
    return f'''      <article class="card" data-cat="{esc(m["cat"].lower())}">
        {icon_html(uri, m["title"][0])}
        <div class="body">
          <h3><a href="{link}" target="_blank" rel="noopener">{esc(m["title"])}</a><span class="cat">{esc(m["cat"])}</span></h3>
          <p class="desc">{esc(m["desc"])}</p>
          {deps_html}
          <div class="foot"><span class="meta">{meta}</span><a class="get" href="{link}" target="_blank" rel="noopener">GitHub &rarr;</a></div>
        </div>
      </article>'''


def apk_card(a):
    uri = normalize_uri(a['iconpath']) if os.path.exists(a['iconpath']) else None
    size = f'{a["bytes"]/1e6:.1f} MB'
    apk_url = f'{FDROID_REPO}/{a["apk"]}'
    return f'''      <article class="card" data-cat="{esc(a["cat"].lower())}">
        {icon_html(uri, a["title"][0])}
        <div class="body">
          <h3>{esc(a["title"])}<span class="cat">{esc(a["cat"])}</span></h3>
          <p class="desc">{esc(a["desc"])}</p>
          <div class="foot"><span class="meta">v{esc(a["ver"])} &middot; {size}</span><span class="sig">xAlisher</span><a class="get" href="{apk_url}">Get APK &darr;</a></div>
        </div>
      </article>'''


def cards(bucket):
    return '\n'.join(bc_card(m) for m in A if m['bucket'] == bucket)


n_cat = sum(1 for m in A if m['bucket'] == 'catalog')
n_unmaintained = sum(1 for m in A if m['bucket'] in ('github', 'untested'))
n_android = len(ANDROID)

catalog_cards = cards('catalog')
unmaintained_cards = cards('github') + '\n' + cards('untested')
android_cards = '\n'.join(apk_card(a) for a in ANDROID)

PAGE = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Alisher&#x27;s apps — Basecamp modules &amp; Android apps</title>
<style>
  :root {{ --bg:#f6f7f9; --card:#fff; --fg:#16181d; --mut:#5b616e; --line:#e4e7ec;
           --accent:#ff0079; --chip:#eef1f5; }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme=light]) {{ --bg:#0f1115; --card:#181b21; --fg:#e8eaed;
      --mut:#9aa1ad; --line:#2a2e37; --accent:#ff4d95; --chip:#232833; }}
  }}
  :root[data-theme=dark] {{ --bg:#0f1115; --card:#181b21; --fg:#e8eaed; --mut:#9aa1ad;
    --line:#2a2e37; --accent:#ff4d95; --chip:#232833; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
    font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif; }}
  header {{ padding:44px 24px 4px; max-width:1080px; margin:0 auto;
    display:flex; align-items:center; gap:16px; }}
  header h1 {{ margin:0; font-size:30px; letter-spacing:-.02em; line-height:1; }}
  header p {{ margin:0; color:var(--mut); }}
  .logo {{ width:46px; height:46px; border-radius:50%; flex:none; text-decoration:none;
    background:#ff0079; box-shadow:0 2px 12px rgba(255,0,121,.42); transition:filter .15s; }}
  .logo:hover {{ filter:brightness(1.12); }}
  .tabs {{ max-width:1080px; margin:22px auto 0; padding:0 24px; display:flex; gap:4px;
    border-bottom:1px solid var(--line); }}
  .tab {{ background:none; border:0; border-bottom:2px solid transparent; color:var(--mut);
    font:inherit; font-weight:600; padding:10px 14px; cursor:pointer; margin-bottom:-1px; }}
  .tab span {{ font-size:12px; background:var(--chip); color:var(--mut); border-radius:999px;
    padding:1px 8px; margin-left:6px; }}
  .tab.on {{ color:var(--fg); border-bottom-color:var(--accent); }}
  .tab.on span {{ background:var(--accent); color:#fff; }}
  .help {{ margin:12px 24px 0; font-size:13px; color:var(--mut); }}
  .help summary {{ cursor:pointer; color:var(--accent); font-weight:600; width:max-content; }}
  .help ol {{ margin:8px 0 0; padding-left:20px; }}
  .help li {{ margin:3px 0; }}
  .help code {{ background:var(--chip); padding:1px 6px; border-radius:5px; word-break:break-all; }}
  .help a {{ color:var(--accent); }}
  .copy {{ margin-left:6px; font-size:11px; padding:1px 8px; border:1px solid var(--line);
    border-radius:6px; background:var(--chip); color:var(--mut); cursor:pointer;
    vertical-align:middle; }}
  .copy:hover {{ color:var(--fg); border-color:var(--accent); }}
  .panel {{ display:none; max-width:1080px; margin:0 auto; }}
  .panel.on {{ display:block; }}
  .ptop {{ display:flex; align-items:center; justify-content:space-between; gap:12px;
    padding:18px 24px 0; color:var(--mut); font-size:13px; flex-wrap:wrap; }}
  .empty {{ padding:26px; color:var(--mut); }}
  main {{ padding:14px 24px 0; display:grid;
    grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:16px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px;
    padding:16px; display:flex; gap:14px; height:190px; }}
  .icon {{ width:56px; height:56px; border-radius:13px; flex:none; object-fit:cover;
    background:var(--chip); }}
  .icon.fallback {{ display:flex; align-items:center; justify-content:center;
    font-weight:700; font-size:24px; color:var(--mut); }}
  .body {{ min-width:0; flex:1; display:flex; flex-direction:column; }}
  .card h3 {{ margin:0 0 4px; font-size:16px; display:flex; align-items:center;
    gap:8px; flex-wrap:wrap; }}
  .card h3 a {{ color:inherit; text-decoration:none; }}
  .card h3 a:hover {{ color:var(--accent); }}
  .cat {{ font-size:11px; font-weight:600; color:var(--mut); background:var(--chip);
    border-radius:6px; padding:2px 7px; text-transform:capitalize; }}
  .desc {{ margin:0 0 8px; color:var(--mut); font-size:13.5px;
    display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }}
  .deps {{ font-size:12px; color:var(--mut); margin-bottom:8px; }}
  .dep {{ background:var(--chip); border-radius:5px; padding:1px 6px; margin-left:4px;
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:11px; }}
  .mod {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:11.5px;
    color:var(--fg); }}
  .foot {{ display:flex; justify-content:flex-start; align-items:center; gap:10px;
    font-size:12px; color:var(--mut); flex-wrap:wrap; margin-top:auto; }}
  .sig {{ color:#059669; white-space:nowrap; }}
  .sig a {{ color:inherit; }}
  .get {{ margin-left:auto; color:var(--accent); font-weight:600; text-decoration:none;
    white-space:nowrap; }}
  .addrepo {{ padding:6px 13px; font-size:13px; border:1px solid var(--accent);
    border-radius:999px; color:var(--accent); text-decoration:none; white-space:nowrap; }}
  .group {{ max-width:1080px; margin:0 auto; }}
  .group > summary {{ cursor:pointer; list-style:none; color:var(--mut); font-weight:600;
    font-size:14px; padding:16px 24px 4px; margin-top:22px; border-top:1px solid var(--line);
    display:flex; align-items:center; gap:9px; }}
  .group > summary::-webkit-details-marker {{ display:none; }}
  .group > summary::before {{ content:"\\25B8"; display:inline-block; transition:transform .15s;
    color:var(--mut); font-size:12px; }}
  .group[open] > summary::before {{ transform:rotate(90deg); }}
  .group > summary .count {{ font-size:12px; background:var(--chip); color:var(--mut);
    border-radius:999px; padding:1px 8px; }}
  .group > summary .note {{ font-weight:400; font-size:12.5px; color:var(--mut); }}
  footer {{ max-width:1080px; margin:0 auto; padding:36px 24px 50px; color:var(--mut);
    font-size:12.5px; }}
  footer code {{ background:var(--chip); padding:1px 6px; border-radius:5px; }}
  footer a {{ color:var(--accent); }}
</style>
</head>
<body>
<header>
  <a class="logo" href="https://alisher.xyz" target="_blank" rel="noopener" title="alisher.xyz" aria-label="alisher.xyz"></a>
  <h1>Alisher&#x27;s apps</h1>
</header>
<div class="tabs">
  <button class="tab on" data-panel="modules">Basecamp <span>{n_cat}</span></button>
  <button class="tab " data-panel="apps">Android <span>{n_android}</span></button>
</div>

<div class="panel on" id="panel-modules">
  <div class="ptop"><span class="sub">{n_cat} Basecamp modules &middot; install with the Package Manager</span></div>
  <details class="help"><summary>How to install</summary><ol><li>Install <a href="https://docs.logos.co/basecamp/install-logos-basecamp">Basecamp</a>, the Logos desktop app.</li><li>Open <b>Package Manager &rarr; Add repository</b> and paste <code>{REPO_JSON}</code><button class="copy" type="button" data-copy="{REPO_JSON}">Copy</button></li><li>Pick a module from the catalog and click <b>Install</b>.</li></ol></details>
  <main>
{catalog_cards}
  </main>
  <details class="group">
    <summary>Not currently maintained on Basecamp <span class="count">{n_unmaintained}</span> <span class="note">&mdash; also on GitHub / archived; may not run on current Basecamp</span></summary>
    <main>
{unmaintained_cards}
    </main>
  </details>
</div>

<div class="panel " id="panel-apps">
  <div class="ptop"><span class="sub">{n_android} Android apps &middot; add the repo in F-Droid for auto-updates</span><a class="addrepo" href="{FDROID_REPO}?fingerprint={FDROID_FP}">+ Add F-Droid repo</a></div>
  <details class="help"><summary>How to install</summary><ol><li>Install the <a href="https://f-droid.org">F-Droid</a> app.</li><li>Tap <b>+ Add F-Droid repo</b> above (or add <code>{FDROID_REPO}</code><button class="copy" type="button" data-copy="{FDROID_REPO}">Copy</button> fingerprint <code>{FDROID_FP}</code>).</li><li>Open the app in F-Droid and tap <b>Install</b>.</li></ol></details>
  <main>
{android_cards}
  </main>
</div>

<footer>
  Basecamp modules install from the <code>lgpd</code> catalog <code>index.json</code>; Android apps
  come from the <a href="{FDROID_REPO}">F-Droid</a> repo &mdash; all built and signed by xAlisher.
  Icons, versions and descriptions come from each published manifest.
</footer>
<script>
  document.querySelectorAll('.tab').forEach(t => t.onclick = () => {{
    document.querySelectorAll('.tab,.panel').forEach(x => x.classList.remove('on'));
    t.classList.add('on');
    document.getElementById('panel-' + t.dataset.panel).classList.add('on');
  }});
  document.querySelectorAll('.copy').forEach(b => b.onclick = () => {{
    navigator.clipboard.writeText(b.dataset.copy).then(() => {{
      var prev = b.textContent; b.textContent = 'Copied!';
      setTimeout(() => {{ b.textContent = prev; }}, 1200);
    }});
  }});
</script>
</body>
</html>'''

open(os.path.join(os.path.dirname(__file__), 'index.html'), 'w').write(PAGE)
print('wrote index.html', len(PAGE), 'bytes ·',
      n_cat, 'catalog ·', n_unmaintained, 'unmaintained (collapsed) ·', n_android, 'android')
