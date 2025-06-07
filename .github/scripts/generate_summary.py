import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import html
import sys


def get_onlinetxt(url):
    for _ in range(3):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
        except requests.RequestException:
            continue
    return ""

def get_title(pdbid):
    url = f"https://data.pdbj.org/pdbjplus/data/pdb/mmjson-noatom/{pdbid}-noatom.json"
    cert_path = os.path.join(os.getcwd(), ".ssl", "pdbj202407.cert")
    for _ in range(3):
        try:
            response = requests.get(url, verify=cert_path, timeout=6.5)
            if response.status_code == 200:
                json_data = response.json()
                name = "data_" + pdbid.upper()
                title = json_data[name]['struct']['title'][0]
                email = json_data[name].get("pdbx_contact_author", {}).get("email", ["zzzzzzz"])[0]
                return pdbid + ": " + title, email
        except requests.RequestException as e:
            print(f"[ERROR] Failed to download {pdbid}. Error: {e}")
    return "error", "error"

def generate_tsv_from_entries(entry_list, output_file_name):
    with open(output_file_name, 'w') as file:
        for count, entry in enumerate(entry_list, start=1):
            print(f"{entry}  No. {count} out of {len(entry_list)} entries.")
            description, email = get_title(entry)
            if description != "error":
                file.write(f"{entry}\t{description}\t{email}\n")

def generate_html_from_tsv(file_name, template_file, modal_block_file, output_file):
    with open(file_name, 'r') as file:
        lines = [line.strip().split('\t') for line in file if line.strip()]
        entries = [(line[0], line[1], line[2]) for line in lines]

    entries = sorted(entries, key=lambda x: x[2])
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Generate thumbnail HTML
    thumbnail_html = ""
    for i, (entry, title, _) in enumerate(entries):
        thumbnail_url = f"https://pdbj.org/molmil-images/mine/{entry}.png"
        safe_title = html.escape(title)
        entry_url = f"https://pdbj.org/mine/summary/{entry}"
        thumbnail_html += f'''
<div onclick="openModal({i})">
  <img src="{thumbnail_url}" alt="{entry}">
  <div class="entry-title">
    <a href="{entry_url}" target="_blank" onclick="event.stopPropagation()">{safe_title}</a>
  </div>
</div>
'''

    # Generate JS array data
    image_data_js = ',\n'.join([
        '{{id: "{0}", src: "https://pdbj.org/molmil-images/mine/{0}.png", title: "{1}", link: "https://pdbj.org/mine/summary/{0}"}}'.format(
            html.escape(entry), html.escape(title.replace('"', '\\"')))
        for entry, title, _ in entries
    ])

    # Load HTML template
    with open(template_file, 'r') as f:
        template = f.read()

    # Load modal + JS and inject entries
    with open(modal_block_file, 'r') as f:
        modal_block = f.read().replace("{{IMAGE_DATA}}", image_data_js)

    # Merge everything
    final_html = template \
        .replace("{{TIMESTAMP}}", now) \
        .replace("{{THUMBNAILS}}", thumbnail_html) \
        .replace("{{MODAL_JS}}", modal_block)

    # Save result
    with open(output_file, "w") as f:
        f.write(final_html)

# === Main Run ===
template_html_path=sys.argv[1]
modal_block_js_path=sys.argv[2]
make_trv=sys.argv[3]
newEntryUrl = "https://pdbj.org/rest/newweb/search/sql?q=select+bs.pdbid+from+pdbj.brief_summary+bs+inner+join+misc.id_meta_list+iml+on+bs.pdbid%3Diml.id+where+iml.category%3D%27pdb_new%27&format=txt"
entry_list = get_onlinetxt(newEntryUrl).strip().split("\n")

tsv_file = "entries.tsv"
if make_trv == "yes":
    generate_tsv_from_entries(entry_list, tsv_file)

generate_html_from_tsv(
    file_name=tsv_file,
    template_file=template_html_path,
    modal_block_file=modal_block_js_path,
    output_file="docs/index.html"
)
