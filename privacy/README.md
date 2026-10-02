# westarrestoration.com

Static site for GitHub Pages. The HTML in this repo is already built; GitHub serves it as-is (`.nojekyll`).

## Edit content
1. Edit `site.json` (phone, email, address, services, cities).
2. Run `pip install jinja2` once, then `python _build/build.py` from the repo root.
3. Commit and push. Every page, the schema, and the sitemap are regenerated.

The red pre-launch banner disappears automatically when no placeholder values remain
(phone `+10000000000`, or any value containing `REPLACE`).

## Before launch
- [ ] Real phone (`phone_display` and `phone_e164`), email, and `legal_name`
- [ ] Address (leave `street` blank to run as a service-area business with no public address)
- [ ] License and certifications (only list ones Westar actually holds)
- [ ] `form_action`: Formspree endpoint (or leave blank to show call/email instead of a form)
- [ ] `ga4_id`
- [ ] Confirm the city list; add 2–3 local paragraphs per city before launch to avoid thin pages
- [ ] Rebuild, push, check every page on the github.io preview

## Deploy
1. Create a GitHub repo, push this folder to `main`.
2. Settings > Pages > Deploy from branch > `main` / root.
3. Custom domain: `westarrestoration.com` (the `CNAME` file is already here).
4. DNS: follow SOP Phase 3 (Cloudflare in front for the 301 and 410 rules).
