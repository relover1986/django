"""
Management command: python manage.py architecture_diagram
Generate full-stack architecture diagram (URL -> View -> Model -> Template)
Outputs interactive HTML with Mermaid.js
"""
import os, re
from django.core.management.base import BaseCommand
from django.urls import get_resolver, URLPattern, URLResolver
from django.conf import settings


def _clean_route(raw):
    """Clean regex route string to human-readable path"""
    # describe() wraps in single quotes: "'^login/$'" → strip them
    if raw.startswith("'") and raw.endswith("'"):
        raw = raw[1:-1]
    # Strip trailing [name='...'] metadata
    if " [name=" in raw:
        raw = raw.split(" [name=")[0]
    s = raw.lstrip("^").rstrip("$")
    # Also strip trailing ' if it leaked from inner quotes
    s = s.strip("'")
    # Replace named groups
    s = re.sub(r"\(\?P<\w+>[^)]+\)", ":id", s)
    # Replace Django path converters <int:xxx> with :id
    s = re.sub(r"<[^>]+>", ":id", s)
    # Remove remaining non-capturing groups
    s = re.sub(r"\([^)]+\)", "", s)
    # Clean double slashes
    s = re.sub(r"/+", "/", s)
    if len(s) > 50:
        s = s[:47] + "..."
    return s if s else "/"


def _sanitize_label(label):
    """Sanitize label for safe embedding in Mermaid [\"...\"] node text"""
    s = label.replace('"', "'")  # Mermaid uses " as delimiter
    s = s.replace("<", "(").replace(">", ")")  # angle brackets confuse parser
    if len(s) > 40:
        s = s[:37] + "..."
    return s.strip()


def extract_urls(resolver, prefix=""):
    results = []
    for pattern in resolver.url_patterns:
        if isinstance(pattern, URLResolver):
            raw = str(pattern.pattern.describe())
            if raw.startswith("'") and raw.endswith("'"):
                raw = raw[1:-1]
            new_prefix = prefix + raw.lstrip("^").rstrip("$")
            results.extend(extract_urls(pattern, new_prefix))
        elif isinstance(pattern, URLPattern):
            raw = str(pattern.pattern.describe())
            route = _clean_route(prefix + raw)
            if not route.startswith("/"):
                route = "/" + route
            callback = pattern.callback
            view_name = str(getattr(callback, "__name__", str(callback)))
            if hasattr(callback, "view_class"):
                vc = callback.view_class
                view_name = f"{vc.__module__}.{vc.__qualname__}"
            elif hasattr(callback, "__module__"):
                view_name = f"{callback.__module__}.{callback.__qualname__}"
            results.append({
                "route": route,
                "name": pattern.name or "",
                "view_name": view_name,
            })
    return results


def analyze_view_source(view_name):
    """Extract model and template references from view source code"""
    models_used = set()
    templates = set()
    parts = view_name.split(".")
    if len(parts) < 2:
        return [], []
    module_path = ".".join(parts[:-1])
    func_or_class = parts[-1]
    try:
        import importlib
        module = importlib.import_module(module_path)
    except Exception:
        return [], []
    obj = getattr(module, func_or_class, None)
    if obj is None:
        return [], []
    try:
        import inspect
        source = inspect.getsource(obj)
    except Exception:
        return [], []
    # template references
    for m in re.finditer(r'render\s*\([^)]*[\x27"]([^\x27"]+\.html)[\x27"]', source):
        templates.add(m.group(1))
    for m in re.finditer(r'template_name\s*=\s*[\x27"]([^\x27"]+)[\x27"]', source):
        templates.add(m.group(1))
    for m in re.finditer(r'get_template\s*\([\x27"]([^\x27"]+\.html)[\x27"]', source):
        templates.add(m.group(1))
    # model references
    for m in re.finditer(r'models\.([A-Z]\w*)', source):
        models_used.add(m.group(1))
    for m in re.finditer(r'([A-Z][a-zA-Z]+)\.objects\.', source):
        models_used.add(m.group(1))
    return sorted(models_used), sorted(templates)


def generate_mermaid(nodes, edges):
    """Generate Mermaid.js flowchart text"""
    lines = ["graph TB"]
    styles = {
        "route": "fill:#1a5276,stroke:#2980b9,color:#fff",
        "view": "fill:#7d3c98,stroke:#af7ac5,color:#fff",
        "model": "fill:#1e8449,stroke:#27ae60,color:#fff",
        "template": "fill:#b7950b,stroke:#f1c40f,color:#fff",
    }
    for t, s in styles.items():
        lines.append(f"  classDef {t} {s}")
    seen_ids = set()
    for n in nodes:
        if n["id"] not in seen_ids:
            seen_ids.add(n["id"])
            label = n["label"].replace('"', "'")
            lines.append(f'  {n["id"]}["{label}"]:::{n["type"]}')
    seen_edges = set()
    for e in edges:
        key = f'{e["from"]}->{e["to"]}'
        if key not in seen_edges:
            seen_edges.add(key)
            if e["label"]:
                lines.append(f'  {e["from"]} -- {e["label"]} --> {e["to"]}')
            else:
                lines.append(f'  {e["from"]} --> {e["to"]}')
    return "\n".join(lines)


HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Django Architecture Diagram</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
<style>
  body{margin:0;background:#1a1a2e;color:#eee;font-family:sans-serif}
  .bar{padding:12px 20px;background:#16213e;border-bottom:1px solid #0f3460;display:flex;align-items:center;gap:16px;flex-wrap:wrap;position:sticky;top:0;z-index:100}
  .bar h1{margin:0;font-size:18px}
  .stats{font-size:13px;color:#888}
  #dia{padding:20px;overflow:auto}
  .mermaid svg{font-size:22px!important;max-width:none!important}
  .mermaid .label{font-size:20px!important;font-weight:600}
  .mermaid .node rect,.mermaid .node circle{stroke-width:3}
  .mermaid .cluster-label text{font-size:18px!important}
</style>
</head>
<body>
<div class="bar">
  <h1>__TITLE__</h1>
  <span class="stats">__STATS__</span>
</div>
<div id="dia"><pre class="mermaid">__DIAGRAM__</pre></div>
<script>
mermaid.initialize({
  startOnLoad:true,theme:"dark",fontSize:22,
  flowchart:{useMaxWidth:false,htmlLabels:true,nodeSpacing:80,rankSpacing:80},
  themeVariables:{
    primaryColor:"#16213e",primaryTextColor:"#eee",
    primaryBorderColor:"#0f3460",lineColor:"#533483",
    secondaryColor:"#0f3460",tertiaryColor:"#1a1a2e",
    fontSize:"22px"
  }
});
</script>
</body>
</html>"""


class Command(BaseCommand):
    help = "Generate full-stack architecture diagram (URL -> View -> Model -> Template)"

    def handle(self, *args, **options):
        resolver = get_resolver()
        urls = extract_urls(resolver)
        self.stdout.write(f"Found {len(urls)} URL patterns")

        nodes, edges = [], []
        for i, u in enumerate(urls):
            rid = f"r{i}"
            models, templates = analyze_view_source(u["view_name"])
            nodes.append({"id": rid, "label": _sanitize_label(u["route"]), "type": "route"})
            vid = f"v{i}"
            short = _sanitize_label(u["view_name"].split(".")[-1])
            nodes.append({"id": vid, "label": short, "type": "view"})
            edges.append({"from": rid, "to": vid, "label": ""})
            for mi, m in enumerate(models):
                nodes.append({"id": f"m{i}_{mi}", "label": _sanitize_label(m), "type": "model"})
                edges.append({"from": vid, "to": f"m{i}_{mi}", "label": "uses"})
            for ti, t in enumerate(templates):
                st = _sanitize_label(t.split("/")[-1])
                nodes.append({"id": f"t{i}_{ti}", "label": st, "type": "template"})
                edges.append({"from": vid, "to": f"t{i}_{ti}", "label": "renders"})

        types = {"route": 0, "view": 0, "model": 0, "template": 0}
        seen = set()
        for n in nodes:
            if n["id"] not in seen:
                seen.add(n["id"])
                types[n["type"]] += 1

        diagram = generate_mermaid(nodes, edges)
        proj = os.path.basename(settings.BASE_DIR)
        html = HTML.replace("__TITLE__", f"{proj} Architecture Diagram")
        html = html.replace("__STATS__",
            f"{types['route']} routes / {types['view']} views / {types['model']} models / {types['template']} templates")
        html = html.replace("__DIAGRAM__", diagram)

        out = os.path.join(settings.BASE_DIR, "architecture_diagram.html")
        with open(out, "w") as f:
            f.write(html)
        self.stdout.write(self.style.SUCCESS(f"Done: {out}"))
        self.stdout.write(
            f"Stats: {types['route']} routes, {types['view']} views, "
            f"{types['model']} models, {types['template']} templates")
