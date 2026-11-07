#!/usr/bin/env python3
"""Measure rendered contrast (computed colors, including overlays) for all themes.

WCAG AA: 4.5:1 for normal text, 3:1 for large text and for non-text UI that
carries meaning only by color is reported separately. Exit 1 if any real text
node fails. Intentional concealments (unopened cloze) are listed, not failed.
"""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/contrast-ld30")
OUT.mkdir(parents=True, exist_ok=True)
PAGES = [p.name for p in sorted(ROOT.glob("*.html"))]
THEMES = ("parchment", "light", "dark")
WIDTHS = (360, 1280)

JS = r"""
() => {
  const parse = (s) => {
    if (!s || s === 'transparent') return null;
    const m = s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x));
    return {r:p[0], g:p[1], b:p[2], a: p.length>3 ? p[3] : 1};
  };
  const blend = (src, dst) => {
    const a = src.a + dst.a * (1 - src.a);
    if (a <= 0) return dst;
    return {
      r: (src.r*src.a + dst.r*dst.a*(1-src.a)) / a,
      g: (src.g*src.a + dst.g*dst.a*(1-src.a)) / a,
      b: (src.b*src.a + dst.b*dst.a*(1-src.a)) / a,
      a: a
    };
  };
  const lum = (c) => {
    const f = (v) => { v/=255; return v<=0.04045 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); };
    return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b);
  };
  const ratio = (fg, bg) => {
    const L1 = lum(fg), L2 = lum(bg);
    const hi = Math.max(L1,L2), lo = Math.min(L1,L2);
    return (hi+0.05)/(lo+0.05);
  };
  const hex = (c) => '#'+[c.r,c.g,c.b].map(v=>Math.round(v).toString(16).padStart(2,'0')).join('');
  const bgOf = (el) => {
    const chain = [];
    for (let e=el; e; e=e.parentElement) chain.push(e);
    chain.reverse();
    let acc = {r:255,g:255,b:255,a:1};
    for (const e of chain) {
      const c = parse(getComputedStyle(e).backgroundColor);
      if (c && c.a>0.01) acc = blend(c, acc);
    }
    const svg = el.closest && el.closest('svg');
    if (svg && (el.tagName === 'text' || el.tagName === 'tspan')) {
      const r = el.getBoundingClientRect();
      const cx = r.left + r.width/2, cy = r.top + r.height/2;
      const shapes = svg.querySelectorAll('rect,circle,ellipse');
      for (let i=shapes.length-1;i>=0;i--) {
        const b = shapes[i].getBoundingClientRect();
        if (cx>=b.left-2 && cx<=b.right+2 && cy>=b.top-2 && cy<=b.bottom+2) {
          const fill = parse(getComputedStyle(shapes[i]).fill);
          if (fill && fill.a>0.05) acc = blend(fill, acc);
          break;
        }
      }
    }
    return acc;
  };
  const skip = (el) => {
    if (!el || el.closest('[hidden]') || el.closest('script,style')) return true;
    if (el.closest('.cloze-blank') && !el.closest('.cloze-blank.open') && !el.classList.contains('open')) return true;
    if (el.classList && (el.classList.contains('cloze-blank') && !el.classList.contains('open'))) return true;
    if (el.classList && el.classList.contains('pl') && el.classList.contains('hid') && !el.classList.contains('open')) return true;
    if (el.tagName==='INPUT' && (el.type==='range' || el.type==='checkbox')) return true;
    if (el.closest('.mem4') && el.classList && el.classList.contains('n')) return true;
    const cs = getComputedStyle(el);
    if (cs.display==='none' || cs.visibility==='hidden') return true;
    let op = 1, e = el;
    while (e && e !== document.documentElement) {
      op *= parseFloat(getComputedStyle(e).opacity || '1');
      e = e.parentElement;
    }
    if (op < 0.85) return true;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return true;
    return false;
  };
  const failures = [], exceptions = [];
  let checked = 0, largeN = 0;
  const seen = new Set();
  const nodes = document.querySelectorAll('h1,h2,h3,h4,p,li,a,button,label,th,td,figcaption,cite,summary,span,b,small,text,input,select,.muted,.chip,.sumline,.spine-note,.q-fb');
  nodes.forEach((el) => {
    if (skip(el)) {
      if (el.classList && (el.classList.contains('cloze-blank') || el.classList.contains('hid') || el.classList.contains('n')))
        exceptions.push(el.className || el.tagName);
      return;
    }
    const text = (el.childNodes.length && [...el.childNodes].some(n=>n.nodeType===3 && n.textContent.trim())) || el.tagName==='text' || el.tagName==='INPUT';
    if (!text && el.tagName!=='text') {
      // still check if element itself has only element children? skip containers to avoid double count
      if (el.tagName!=='TEXT' && el.children.length) return;
    }
    const raw = (el.innerText || el.textContent || el.getAttribute('placeholder') || el.value || '').trim();
    if (!raw) return;
    const cs = getComputedStyle(el);
    const svgText = el.tagName==='text' || el.tagName==='tspan';
    const fg0 = svgText ? (parse(cs.fill) || parse(cs.color)) : parse(cs.color);
    if (!fg0 || fg0.a < 0.2) { exceptions.push('transparent-ink '+el.tagName); return; }
    const bg = bgOf(el);
    const fg = blend(fg0, bg);
    const size = parseFloat(cs.fontSize)||16;
    const weight = parseInt(cs.fontWeight,10)||400;
    const large = size>=24 || (size>=18.66 && weight>=700);
    const need = large ? 3 : 4.5;
    const got = ratio(fg, bg);
    checked++;
    if (large) largeN++;
    if (got + 0.02 < need) {
      const key = hex(fg)+hex(bg)+el.tagName+(el.className&&el.className.baseVal===undefined?el.className:el.className)+raw.slice(0,24);
      if (seen.has(key)) return;
      seen.add(key);
      if (failures.length<60) failures.push({
        tag: el.tagName, cls: String(el.className&&el.className.baseVal!==undefined?'':el.className).slice(0,80),
        text: raw.slice(0,42), ratio: Math.round(got*100)/100, need, large,
        fg: hex(fg), bg: hex(bg), size
      });
    }
  });
  return {checked, largeN, failCount: failures.length, failures, exceptionSample: exceptions.slice(0,8)};
}
"""

report = {"pages": [], "failures": 0, "checked": 0}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--disable-gpu"])
    for theme in THEMES:
        for width in WIDTHS:
            for name in PAGES:
                if width == 360 and name not in ("index.html", "sermon.html", "table.html", "memorize.html", "compare.html", "hc.html"):
                    continue
                ctx = b.new_context(viewport={"width": width, "height": 900})
                page = ctx.new_page()
                page.goto((ROOT / name).as_uri())
                page.evaluate("t=>document.documentElement.setAttribute('data-theme',t)", theme)
                page.wait_for_timeout(40)
                page.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))")
                page.evaluate("document.body.setAttribute('data-toc','closed')")
                if name == "memorize.html":
                    page.click("#fc", position={"x": 20, "y": 20}, force=True)
                    page.wait_for_timeout(400)
                    if page.query_selector(".cloze-blank"):
                        page.click(".cloze-blank", force=True)
                    if page.query_selector("#quiz-ser .q-opts button"):
                        page.click("#quiz-ser .q-opts button", force=True)
                        page.wait_for_timeout(100)
                if name == "creeds-read.html":
                    page.click("#modes button[data-mode=cloze]", force=True)
                    page.wait_for_timeout(200)
                    if page.query_selector(".cloze-blank"):
                        page.click(".cloze-blank", force=True)
                if page.query_selector("[data-viz-i='1']"):
                    page.click("[data-viz-i='1']", force=True)
                    page.wait_for_timeout(80)
                if width < 1100 and page.query_selector("#toc"):
                    page.evaluate("document.body.setAttribute('data-toc','open')")
                link = page.query_selector("main p a, main .linklist a, main a")
                if link:
                    try:
                        link.hover(force=True, timeout=2000)
                    except Exception:
                        pass
                data = page.evaluate(JS)
                data.update(page=name, theme=theme, width=width)
                report["pages"].append({k: data[k] for k in ("page", "theme", "width", "checked", "failCount")})
                report["checked"] += data["checked"]
                if data["failures"]:
                    report["failures"] += len(data["failures"])
                    report.setdefault("items", []).extend([{**f, "page": name, "theme": theme, "width": width} for f in data["failures"]])
                ctx.close()
    # print media spot-check
    ctx = b.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    page.goto((ROOT / "sermon.html").as_uri())
    page.emulate_media(media="print")
    page.evaluate("document.documentElement.setAttribute('data-theme','parchment')")
    printed = page.evaluate(JS)
    report["print"] = {"checked": printed["checked"], "failCount": printed["failCount"], "failures": printed["failures"][:15]}
    report["failures"] += printed["failCount"]
    ctx.close()
    b.close()

(OUT / "contrast-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
lines = ["# Contrast audit", "", f"Checked text samples: {report['checked']}", f"Failure groups: {report['failures']}", ""]
if report.get("items"):
    lines.append("| page | theme | width | ratio | need | sample | fg | bg |")
    lines.append("|---|---|---:|---:|---:|---|---|---|")
    for f in report["items"][:80]:
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (f["page"], f["theme"], f["width"], f["ratio"], f["need"], f["text"].replace("|","/"), f["fg"], f["bg"]))
else:
    lines.append("No measured text nodes fell below the AA threshold in this run.")
lines += ["", "Intentional exceptions (not failures): unopened cloze blanks stay transparent until revealed; the large decorative index on memory cards is opacity 0.2; closed mobile nav is opacity 0.", "Print pass is included for sermon.html."]
(OUT / "contrast-report.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
print("\n".join(lines[:12]))
print("items", len(report.get("items") or []))
sys.exit(1 if report["failures"] else 0)
