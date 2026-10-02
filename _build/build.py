"""Builds the static site from site.json.  Usage (from repo root):  python _build/build.py
Requires: pip install jinja2"""
import json, datetime, os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "site.json").read_text())
b, cities, services = data["business"], data["cities"], data["services"]
env = Environment(loader=FileSystemLoader(ROOT / "_build" / "templates"),
                  autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)

ICONS = {
 "water-damage": '<svg viewBox="0 0 24 24"><path d="M12 3c3 4.5 6 7.6 6 11a6 6 0 0 1-12 0c0-3.4 3-6.5 6-11z"/></svg>',
 "fire-smoke-damage": '<svg viewBox="0 0 24 24"><path d="M12 3c1 3 4 5 4 9a4 4 0 0 1-8 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3-1-5 0-8z"/></svg>',
 "mold-remediation": '<svg viewBox="0 0 24 24"><circle cx="8" cy="9" r="2.5"/><circle cx="15" cy="7" r="1.8"/><circle cx="14" cy="14" r="3"/><circle cx="7" cy="16" r="1.6"/></svg>',
 "sewage-cleanup": '<svg viewBox="0 0 24 24"><path d="M5 9h14v3a7 7 0 0 1-14 0zM9 9V5h6v4"/></svg>',
 "storm-damage": '<svg viewBox="0 0 24 24"><path d="M6 13a4 4 0 0 1 1-7.9A5 5 0 0 1 17 6a3.5 3.5 0 0 1 1 7zM12 13l-2 4h3l-2 4"/></svg>',
}
placeholders = "0000000" in b["phone_e164"] or "REPLACE" in json.dumps(b)
year = datetime.date.today().year
base_ctx = dict(b=b, cities=cities, services=services, placeholders=placeholders, year=year, icons=ICONS)
pages = []

def biz_schema():
    s = {"@context": "https://schema.org", "@type": "HomeAndConstructionBusiness", "@id": b["domain"] + "/#business",
         "name": b["name"], "url": b["domain"] + "/", "telephone": b["phone_e164"], "email": b["email"],
         "openingHoursSpecification": {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], "opens": "00:00", "closes": "23:59"},
         "areaServed": [{"@type": "City", "name": c["name"] + ", CA"} for c in cities]}
    if b["street"]:
        s["address"] = {"@type": "PostalAddress", "streetAddress": b["street"], "addressLocality": b["city"],
                        "addressRegion": b["region"], "postalCode": b["postal"], "addressCountry": "US"}
    if "REPLACE" not in b["legal_name"]: s["legalName"] = b["legal_name"]
    return s

def crumbs_schema(crumbs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": b["domain"] + p} for i, (n, p) in enumerate(crumbs)]}

def render(tpl, path, title, description, schemas=(), crumbs=None, **ctx):
    sch = list(schemas) + ([crumbs_schema(crumbs)] if crumbs else [])
    html = env.get_template(tpl).render(**base_ctx, **ctx, path=path, title=title, description=description,
                                        crumbs=crumbs, schemas=[json.dumps(s, ensure_ascii=False).replace("</", "<\\/") for s in sch])
    out = ROOT / path.strip("/") / "index.html" if path != "/404.html" else ROOT / "404.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    if path != "/404.html": pages.append(path)

HOME = ("Home", "/")
# Home
triage = {s["slug"]: {"name": s["name"], "now": s["now"], "url": f"/services/{s['slug']}/"} for s in services if s["now"]}
render("home.html", "/", f"{b['name']} | 24/7 Water, Fire & Mold Damage Restoration",
       "24/7 water, fire, mold, sewage, and storm damage restoration in " + ", ".join(c["name"] for c in cities) + ". Call now for emergency service.",
       schemas=[biz_schema(), {"@context": "https://schema.org", "@type": "WebSite", "name": b["name"], "url": b["domain"] + "/"}],
       section="home", triage_json=json.dumps(triage).replace("</", "<\\/"))

# Services
for s in services:
    cr = [HOME, ("Services", "/services/"), (s["name"], f"/services/{s['slug']}/")]
    sch = [{"@context": "https://schema.org", "@type": "Service", "name": s["name"], "description": s["summary"],
            "provider": {"@id": b["domain"] + "/#business"}, "areaServed": [c["name"] + ", CA" for c in cities]}]
    if s["faqs"]:
        sch.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in s["faqs"]]})
    render("service.html", f"/services/{s['slug']}/", f"{s['name']} | {b['name']}", s["summary"],
           schemas=sch, crumbs=cr, section="services", s=s, h1=s["name"], city=None)

svc_body = '<ul class="svc-list">' + "".join(
    f'<li><a href="/services/{s["slug"]}/"><span class="svc-name">{s["name"]}</span><span class="svc-sum">{s["summary"]}</span></a></li>' for s in services) + "</ul>"
render("simple.html", "/services/", f"Restoration services | {b['name']}",
       "Water damage, fire and smoke, mold remediation, sewage cleanup, storm damage, and reconstruction.",
       crumbs=[HOME, ("Services", "/services/")], section="services", h1="Restoration services",
       lede="Emergency response and the full repair afterward.", body=svc_body, show_lead=True)

# Cities
for c in cities:
    cr = [HOME, ("Service areas", "/service-areas/"), (c["name"], f"/service-areas/{c['slug']}/")]
    sch = [{"@context": "https://schema.org", "@type": "Service", "name": f"Damage restoration in {c['name']}",
            "provider": {"@id": b["domain"] + "/#business"}, "areaServed": {"@type": "City", "name": c["name"] + ", CA"}}]
    render("city.html", f"/service-areas/{c['slug']}/", f"Water & Fire Damage Restoration in {c['name']}, CA | {b['name']}",
           f"24/7 water, fire, mold, and storm damage restoration in {c['name']}, {c['county']}. Call {b['phone_display']}.",
           schemas=sch, crumbs=cr, section="areas", city=c)

area_body = '<ul class="city-list">' + "".join(f'<li><a href="/service-areas/{c["slug"]}/">{c["name"]}</a></li>' for c in cities) + \
            "</ul><p>Outside these cities? Call and we'll tell you whether we can reach you.</p>"
render("simple.html", "/service-areas/", f"Service areas | {b['name']}", "Cities we serve for emergency restoration.",
       crumbs=[HOME, ("Service areas", "/service-areas/")], section="areas", h1="Service areas", lede="", body=area_body, show_lead=False)

# About / contact / privacy / 404
certs = "".join(f"<li>{x}</li>" for x in b["certifications"])
about_body = (f"<p>{b['name']} handles the emergency and the rebuild: water extraction and drying, fire and smoke cleanup, mold remediation, "
              "sewage cleanup, storm repairs, and reconstruction.</p><p>We document every job with photos and moisture readings so your "
              "insurance claim has what it needs, and we explain each step before we take it.</p>"
              + (f"<h2>Certifications</h2><ul>{certs}</ul>" if certs else ""))
render("simple.html", "/about/", f"About | {b['name']}", f"About {b['name']}, 24/7 damage restoration.",
       crumbs=[HOME, ("About", "/about/")], section="about", h1=f"About {b['name']}", lede="", body=about_body, show_lead=True)
contact_body = (f'<p class="big-phone"><a href="tel:{b["phone_e164"]}">{b["phone_display"]}</a></p><p>Answered 24 hours a day, every day.</p>'
                f'<p>Email: <a href="mailto:{b["email"]}">{b["email"]}</a></p>')
render("simple.html", "/contact/", f"Contact | {b['name']}", f"Call {b['name']} 24/7 at {b['phone_display']}.",
       crumbs=[HOME, ("Contact", "/contact/")], section="contact", h1="Contact us", lede="", body=contact_body, show_lead=True)
priv = ("<p>We collect the information you send us (name, phone, city, and message) only to respond to your request. "
        "We don't sell it. Phone calls may be tracked or recorded for quality and to attribute calls to our marketing.</p>"
        "<p>This site uses analytics cookies to understand traffic. To ask what we hold about you or to delete it, "
        f'email <a href="mailto:{b["email"]}">{b["email"]}</a>.</p>')
render("simple.html", "/privacy/", f"Privacy | {b['name']}", "Privacy policy.", crumbs=[HOME, ("Privacy", "/privacy/")],
       section="", h1="Privacy", lede="", body=priv, show_lead=False)
render("simple.html", "/404.html", f"Page not found | {b['name']}", "Page not found.", section="", h1="That page isn't here",
       lede="If you have an emergency, call now.", body=f'<p><a class="btn btn-call" href="tel:{b["phone_e164"]}">Call {b["phone_display"]}</a></p><p><a href="/">Go to the homepage</a></p>', show_lead=False)

# sitemap / robots / CNAME
today = datetime.date.today().isoformat()
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url><loc>{b['domain']}{p}</loc><lastmod>{today}</lastmod></url>\n" for p in pages if p != "/privacy/") + "</urlset>\n"
(ROOT / "sitemap.xml").write_text(sm)
(ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {b['domain']}/sitemap.xml\n")
(ROOT / "CNAME").write_text(b["domain"].replace("https://", "") + "\n")
(ROOT / ".nojekyll").write_text("")
print(f"Built {len(pages)+1} pages. Placeholders present: {placeholders}")
