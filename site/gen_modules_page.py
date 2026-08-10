#!/usr/bin/env python3
"""Generate modules.alisher.xyz/index.html — Basecamp-style catalog landing page."""
import base64, glob, os, html, re

BASE = os.path.expanduser('~/basecamp/modules')
GH = "https://github.com/xAlisher"

def icon_data_uri(module_dir, hint):
    cands = []
    if hint:
        cands += glob.glob(f'{module_dir}/{hint}') + glob.glob(f'{module_dir}/**/{hint}', recursive=True)
    cands += glob.glob(f'{module_dir}/**/*.png', recursive=True) + glob.glob(f'{module_dir}/**/*.svg', recursive=True)
    for p in cands:
        low = p.lower()
        if any(x in low for x in ('demo','screenshot','listener','host-stream','social','sidebar','preview')):
            continue
        try:
            b = open(p, 'rb').read()
            if len(b) > 300_000: continue
            mime = 'image/svg+xml' if p.endswith('.svg') else 'image/png'
            return f'data:{mime};base64,' + base64.b64encode(b).decode()
        except Exception: continue
    return None

# bucket: catalog | github | untested   |   mods = package names bundled in the repo
A = [
 # ── in this repository (catalog, tested on 0.2.x) ──
 dict(bucket='catalog', repo='docs-logos', dir='', title='Docs', ver='0.1.0', iface='Universal',
      cat='Utility', core=[], icon='', mods=['docs_logos'],
      iconpath=os.path.expanduser('~/docs-assistant/qml/icon.png'),
      desc='Search the Basecamp & Logos docs and blog from inside Basecamp — on-device BM25 keyword search with a full-screen Markdown reader (code blocks, tables, copyable text), recency-aware ranking, and an in-module crawler that rebuilds the index on demand. Linux + macOS.'),
 dict(bucket='catalog', repo='logos-blockchain-ui', dir='', title='Blockchain node', ver='0.2.6', iface='Universal',
      cat='Blockchain', core=[], icon='', mods=['logos_node_1click','blockchain_module'],
      desc='Community 1-click fork — run a Logos blockchain node on the testnet in one click: sync to the tip, monitor and manage. Renders on Basecamp v0.2.3, syncs the 0.2.1 testnet. Live Blend Network status line (edge / core / broadcast, with honest per-epoch detail). Proposals tab (blocks your node proposed) with a durable history that survives log pruning, leadership voucher count, LGO-formatted balances, a borderless dashboard, and a node settings modal.'),
 dict(bucket='catalog', repo='ia-basecamp', dir='', title='Archive', ver='0.2.0', iface='Legacy',
      cat='Archiving', core=['Storage','Blockchain'], icon='archive.png', mods=['archive','archive_ui'],
      desc='Follow curated LEZ channels and preserve their Internet Archive collections to Logos Storage.'),
 dict(bucket='catalog', repo='receiver-basecamp', dir='', title='Receiver', ver='0.3.0', iface='Universal',
      cat='Streaming', core=['Messaging'], icon='', mods=['receiver_ui'],
      desc='Discover and listen to decentralized Logos radio broadcasts over LogosMessaging, via Tor. Zero-install: bundles its own ffplay + Tor, no deps to install (Linux + macOS).'),
 dict(bucket='catalog', repo='booth-basecamp', dir='', title='Booth (xRadio)', ver='0.2.1', iface='Universal',
      cat='Streaming', core=['Messaging'], icon='', mods=['radio_ui','radio_module'],
      desc='Broadcast your own decentralized station — RTMP → MediaMTX, announced over delivery.'),
 dict(bucket='catalog', repo='lez-stark-verify', dir='', title='ZK Guess', ver='0.1.1', iface='Universal',
      cat='Game', core=['Messaging'], icon='', mods=['zk_guess_game'],
      iconpath=os.path.expanduser('~/lez-stark-verify/module/zk-guess-game/qml/icon.png'),
      desc='Provably-fair number-guessing party game — the machine proves above/below without revealing the number, then settles the win on-zone (STARK-verified on the Logos Execution Zone).'),
 # ── also on GitHub (works on 0.2.x, install from source) ──
 dict(bucket='github', repo='keeper-basecamp', dir='', title='Keeper', ver='0.2.0', iface='Universal',
      cat='Archiving', core=['Storage','Blockchain'], icon='keeper.png', mods=['keeper'],
      desc='Preserve Internet Archive collections — download, store CIDs on Logos Storage, inscribe on-chain.'),
 dict(bucket='github', repo='beacon-basecamp', dir='', title='Beacon', ver='2.0.0', iface='Universal',
      cat='Blockchain', core=['Blockchain'], icon='', mods=['logos_beacon'],
      desc='On-chain CID inscription — sequence content references onto the Logos Execution Zone.'),
 dict(bucket='github', repo='stash-basecamp', dir='', title='Stash', ver='0.1.0', iface='Universal',
      cat='Storage', core=['Storage'], icon='', mods=['stash'],
      iconpath=os.path.expanduser('~/basecamp/modules/stash-basecamp/plugins/stash_ui/qml/icons/Stash_sidebar.png'),
      desc='Connects decentralised storage (Kubo, Pinata or Logos) to your module.'),
 dict(bucket='github', repo='keycard-basecamp', dir='', title='Keycard', ver='1.0.0', iface='Legacy',
      cat='Security', core=[], icon='keycard.png', mods=['keycard'],
      desc='Smartcard authentication — unlock and sign with a hardware Keycard.'),
 dict(bucket='github', repo='qr-basecamp', dir='', title='QR', ver='0.2.0', iface='Universal',
      cat='Utility', core=[], icon='', mods=['qr'],
      desc='Generate and scan QR codes inside Basecamp — share CIDs, keys and links.'),
 # ── not tested in Basecamp 0.2.x ──
 dict(bucket='untested', repo='cord-basecamp', dir='', title='Cord', ver='1.0.0', iface='Legacy',
      cat='Social', core=['Messaging','Blockchain'], icon='cord.png', mods=['logos_cord'],
      desc='Social layer — subscribe to Beacon channels and follow on-chain publishers.'),
 dict(bucket='untested', repo='logos-notes', dir='', title='Notes', ver='1.0.0', iface='Legacy',
      cat='Productivity', core=['Storage'], icon='', mods=['notes'],
      iconpath=os.path.expanduser('~/basecamp/modules/logos-notes/plugins/notes_ui/qml/icons/notes.png'),
      desc='Encrypted, local-first notes for the Logos ecosystem.'),
 dict(bucket='untested', repo='logos-wallet-basecamp', dir='', title='Wallet', ver='0.1.0', iface='Legacy',
      cat='Finance', core=['Blockchain'], icon='', mods=['logos_wallet'],
      desc='Native token wallet — accounts, faucet, and keycard-gated transfers.'),
 dict(bucket='untested', repo='soulseek-basecamp', dir='', title='Soulseek', ver='0.1.0', iface='Legacy',
      cat='Music', core=[], icon='', mods=['soulseek'],
      desc='Soulseek music search, download, and playlist management.'),
 dict(bucket='untested', repo='scorched-earth', dir='', title='Scorched Earth', ver='0.1.0', iface='Legacy',
      cat='Game', core=['Messaging'], icon='', mods=['scorched_earth','scorched_earth_ui'],
      iconpath=os.path.expanduser('~/basecamp/modules/scorched-earth/scorched-earth-ui/icons/scorched-earth.png'),
      desc='Turn-based artillery game — hot-seat or P2P multiplayer over Waku, no server or accounts.'),
 dict(bucket='untested', repo='logos-snake-game', dir='', title='Snake', ver='1.0.0', iface='Legacy',
      cat='Game', core=[], icon='', mods=['snake_game'],
      desc='The classic Snake — a Basecamp mini-game.'),
 dict(bucket='untested', repo='logos-node-basecamp', dir='', title='Logos Node', ver='0.1.0', iface='Legacy',
      cat='Infrastructure', core=['Blockchain'], icon='', mods=['logos_node','node_ui'],
      desc='Run and manage a Logos blockchain node from inside Basecamp.'),
]

def file_data_uri(p):
    b = open(p, 'rb').read()
    mime = 'image/svg+xml' if p.endswith('.svg') else 'image/png'
    return f'data:{mime};base64,' + base64.b64encode(b).decode()

def card(m):
    d = f'{BASE}/{m["repo"]}' + (f'/{m["dir"]}' if m['dir'] else '')
    uri = file_data_uri(m['iconpath']) if m.get('iconpath') and os.path.exists(m['iconpath']) else icon_data_uri(d, m['icon'])
    letter = m['title'][0]
    cls = ' class="glyph"' if m.get('glyph') else ''
    icon = (f'<img src="{uri}"{cls} alt="">' if uri else f'<span class="ic-fallback">{letter}</span>')
    ifc = 'universal' if m['iface']=='Universal' else 'legacy'
    core = ''.join(f'<span class="chip">{html.escape(c)}</span>' for c in m['core']) or '<span class="chip chip-none">standalone</span>'
    bundle = ''
    if len(m['mods']) > 1:
        mods = ' · '.join(f'<code>{html.escape(x)}</code>' for x in m['mods'])
        bundle = f'<div class="bundle"><span class="b-lbl">bundles</span>{mods}</div>'
    return f'''<article class="card">
  <div class="card-top">
    <div class="ic">{icon}</div>
    <div class="card-head">
      <div class="title-row"><h3>{html.escape(m["title"])}</h3><span class="ver">v{m["ver"]}</span></div>
      <div class="pills"><span class="pill pill-{ifc}">{m["iface"]}</span><span class="pill pill-cat">{html.escape(m["cat"])}</span></div>
    </div>
  </div>
  {bundle}
  <p class="desc">{html.escape(m["desc"])}</p>
  <div class="uses"><span class="uses-label">Uses</span>{core}</div>
  <a class="repo-link" href="{GH}/{m["repo"]}" target="_blank" rel="noopener">GitHub<span class="arr">→</span></a>
</article>'''

def cards(bucket): return '\n'.join(card(m) for m in A if m['bucket']==bucket)

# clean QR svg → responsive (drop mm width/height, keep viewBox)
qr = open('/tmp/qr.svg').read()
qr = re.sub(r'width="[^"]*"', '', qr, count=1)
qr = re.sub(r'height="[^"]*"', '', qr, count=1)
qr = qr.replace("<?xml version='1.0' encoding='UTF-8'?>", '').strip()

TPL = open(os.path.join(os.path.dirname(__file__), 'page_template.html')).read()
out = (TPL.replace('{{CATALOG_CARDS}}', cards('catalog'))
          .replace('{{GITHUB_CARDS}}', cards('github'))
          .replace('{{UNTESTED_CARDS}}', cards('untested'))
          .replace('{{QR}}', qr))
open(os.path.join(os.path.dirname(__file__), 'index.html'), 'w').write(out)
print('wrote index.html', len(out), 'bytes ·',
      len([m for m in A if m['bucket']=='catalog']),'catalog',
      len([m for m in A if m['bucket']=='github']),'github',
      len([m for m in A if m['bucket']=='untested']),'untested')
