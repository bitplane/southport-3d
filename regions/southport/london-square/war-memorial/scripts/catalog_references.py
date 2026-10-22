"""Catalog observed reference image links from downloaded public source pages."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote, urljoin
import json
import re

ROOT = Path(__file__).resolve().parents[1]


class IWMImages(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.html = html
        self.items = []

    def handle_starttag(self, tag, attrs):
        if tag != "img":
            return
        a = dict(attrs)
        src = a.get("src", "")
        marker = "/styles/thumbnail/public/"
        if marker not in src:
            return
        original = src.split("?")[0].replace(marker, "/")
        # Original file paths are explicitly present in the embedded gallery data.
        assert urlparse(original).path in self.html
        name = Path(urlparse(original).path).name
        caption = a.get("alt", "")
        deferred = any(s in caption.lower() for s in ("pedestal altar", "cenotaph crest", "cenotaph at", "gardens", "ww2 dates", "plaques"))
        self.items.append({
            "id": "iwm-" + Path(name).stem,
            "provider": "Imperial War Museums War Memorials Register",
            "source_page": "https://memorials.iwm.org.uk/memorial/1228",
            "image_url": original,
            "caption": caption,
            "local_file": "references/images/iwm-" + name,
            "scope": "deferred_or_context" if deferred else "exterior_reference",
            "capture_date": None,
            "notes": "IWM captions simplify compass directions; reconcile against true site orientation. Reference photograph, not a distributable model texture.",
        })


class WMOImages(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        original = a.get("data-original-src", "")
        if tag == "img" and original:
            name = Path(unquote(urlparse(original).path)).name
            self.items.append({
                "id": "wmo-" + re.sub(r"[^A-Za-z0-9_-]", "_", Path(name).stem),
                "provider": "War Memorials Online",
                "source_page": "https://www.warmemorialsonline.org.uk/memorial/140024",
                "image_url": urljoin("https://www.warmemorialsonline.org.uk", original),
                "local_file": "references/images/wmo-" + re.sub(r"[^A-Za-z0-9_.-]", "_", name),
                "scope": "unreviewed",
            })


iwm_html = (ROOT / "references/pages/iwm-1228.html").read_text()
iwm = IWMImages(iwm_html)
iwm.feed(iwm_html)
decoded=iwm_html.replace('\\"','"')
for item in iwm.items:
    path=urlparse(item['image_url']).path
    end=decoded.find('"url":"'+path+'"')
    start=decoded.rfind('"type":"media--image"',0,end)
    chunk=decoded[start:end]
    for field in ('credit','copyright','licence','description'):
        match=re.search(r'"field_media_'+field+r'":(null|"[^"\n]*")',chunk)
        if match:item[field]=json.loads(match.group(1))
    if item['id']=='iwm-mont_8':item['corrected_location']='NE colonnade SE end; IWM image caption reversed, confirmed by HE and inscription prose'
    if item['id']=='iwm-mont_8a':item['corrected_location']='SW colonnade SE end; IWM image caption reversed, confirmed by WMO Southport_2 and HE'
wmo = WMOImages()
wmo.feed((ROOT / "references/pages/wmo-140024.html").read_text())
data = {
    "retrieved_at_utc": "2026-10-21",
    "intended_use": "Visual evidence for traced and authored geometry, including bounded shading-derived relief detail where explicitly documented; source colour is not embedded in models. Retain source credits.",
    "images": iwm.items + wmo.items,
}
supplemental=ROOT/'research/supplemental_sources.json'
if supplemental.exists():
    extra=json.loads(supplemental.read_text())
    data['images'].extend(extra['images'])
    data['documents']=extra.get('documents',[])
(ROOT / "research/reference_catalog.json").write_text(json.dumps(data, indent=2) + "\n")
selected = [i for i in iwm.items if i["scope"] == "exterior_reference"]
print('Catalogued',len(iwm.items),'IWM images and',len(wmo.items),'WMO images, with available IWM credits.')
