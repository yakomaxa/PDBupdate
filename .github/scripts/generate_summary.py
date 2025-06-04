import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
def get_onlinetxt(url):
    count = 0
    for _ in range(0,3):
        try:
            response = requests.get(url)
            # Check if the request was successful
            if response.status_code == 200:
                content = response.text
                return content
        except requests.RequestException as e:
            print(f"Failed to retrieve the file. HTTP Status Code: {response.status_code}")
            count += 1
            if count >= 3:
                return 0

def get_title(pdbid):
    url = "https://data.pdbj.org/pdbjplus/data/pdb/mmjson-noatom/" + pdbid + "-noatom.json"
    cwd = os.getcwd()
    cert_path = cwd + "/.ssl/" + "pdbj202407.cert"    
    #https://data.pdbj.org/pdbjplus/data/pdb/mmjson-noatom/9bgp-noatom.json
    # probably changed around the head of 2024 July
    #url = "https://data.pdbjbk1.pdbj.org/pdbjplus/data/pdb/mmjson-noatom/"+ pdbid + "-noatom.json"
    #response = requests.get(url,verify=False) # temporary workaround
    count = 0
    failing = True
    path = ""
    while failing or count <= 3 :        
            try:
                response = requests.get(url,verify=cert_path,timeout=6.5) # temporary workaround
                failing = False
                if response.status_code == 200:
                    json_data = response.json()
                    name = "data_" + pdbid.upper()
                    title=json_data[name]['struct']['title'][0]
                    if "pdbx_contact_author" in json_data[name]:
                        email = json_data[name]["pdbx_contact_author"]['email'][0]
                    else:
                        email = "zzzzzzz"
                        print(title)
                    return pdbid+":"+title, email
                else:
                    print(f"Failed to retrieve the JSON data. HTTP Status Code: {response.status_code}")
                    return "error", "error"
            except requests.RequestException as e:
                print(f"[ERROR] Failed to download {pdbid}. Error: {e}")
                count += 1
    
def generate_tsv_from_entries(entry_list, output_file_name):
    """Generate a .tsv file with entries and their respective descriptions."""
    with open(output_file_name, 'w') as file:
        count = 0
        length = len(entry_list)
        for entry in entry_list:
            #if count >= 10: debug
            # break
            count += 1            
            print(entry + "  No. " + str(count) + " out of " + str(length) + " entries.")
            output = get_title(entry)
            print(output)
            if output[0] is None or output[1] is None:
                print(f"email or description is missing in  {entry}")
            else:
                email = output[1]
                description = output[0]
                if description and email:
                    file.write(f"{entry}\t{description}\t{email}\n")
                else:
                    print(f"Warning: Could not fetch description for {entry}")



def generate_html_from_tsv(file_name):
    from datetime import datetime
    import html

    with open(file_name, 'r') as file:
        lines = [line.strip().split('\t') for line in file]
        entries = [(line[0], line[1], line[2]) for line in lines]

    entries = sorted(entries, key=lambda x: x[2])
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    image_data_js = ',\n'.join([
        '{{id: "{0}", src: "https://pdbj.org/molmil-images/mine/{0}.png", title: "{1}", link: "https://pdbj.org/mine/summary/{0}"}}'.format(
            html.escape(entry), html.escape(title.replace('"', '\\"')))
        for entry, title, _ in entries
    ])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>PDBj Updates</title>
<style>
    body {{
        font-family: sans-serif;
        margin: 0;
    }}

    .thumbnail-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 16px;
        padding: 20px;
    }}

    .thumbnail-grid img {{
        max-width: 100%;
        height: auto;
        border: 1px solid #ddd;
        border-radius: 4px;
        padding: 5px;
        transition: transform 0.2s;
        cursor: pointer;
    }}

    .thumbnail-grid img:hover {{
        transform: scale(1.1);
    }}

    .entry-title {{
        text-align: center;
        font-size: 14px;
        margin-top: 8px;
    }}

    #modal {{
        display: none;
        position: fixed;
        z-index: 999;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.9);
        justify-content: center;
        align-items: center;
        flex-direction: column;
        overflow-y: auto;
        padding: 20px;
    }}

    #modal img {{
        margin: 10px 0;
        max-width: 95vw;
        max-height: 80vh;
        border: 1px solid #888;
    }}

    .modal-title {{
        color: white;
        margin-top: 10px;
        font-size: 18px;
    }}

    .nav-button {{
    position: fixed;               /* fixed to viewport, not modal content */
    top: 50%;                      /* center vertically */
    transform: translateY(-50%);   /* adjust for own height */
    font-size: 2.5rem;
    color: white;
    background: none;
    border: none;
    cursor: pointer;
    user-select: none;
    z-index: 1001;
    padding: 0 10px;
}}

.prev {{
    left: 20px;
}}

.next {{
    right: 20px;
}}
    .close {{
        position: absolute;
        top: 8%;                      /* center vertically */
        right: 8%;
        font-size: 2rem;
        color: white;
        cursor: pointer;
    }}

    .rcsb-image {{
    max-width: 150px;
    height: auto;
    border: 1px solid #888;
    margin: 10px 0;
    }}


    #pdbeViews {{
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        margin-top: 10px;
    }}

    #pdbeViews img {{
        max-width: 100%;
        height: auto;
        border: 1px solid #666;
    }}
</style>
</head>
<body>
<div style="text-align:center;">Updated at {now}</div>
<div class="thumbnail-grid">
"""

    for i, (entry, title, _) in enumerate(entries):
        thumbnail_url = f"https://pdbj.org/molmil-images/mine/{entry}.png"
        safe_title = html.escape(title)
        entry_url = f"https://pdbj.org/mine/summary/{entry}"
        html_content += f'''
<div onclick="openModal({i})">
  <img src="{thumbnail_url}" alt="{entry}">
  <div class="entry-title">
    <a href="{entry_url}" target="_blank" onclick="event.stopPropagation()">{safe_title}</a>
  </div>
</div>
'''

    html_content += """
</div>

<!-- Modal Overlay -->
<div id="modal">
  <span class="close" onclick="closeModal()">&times;</span>
  <button class="nav-button prev" onclick="prevImage()">&#10094;</button>

  <a id="modalLink" href="#" target="_blank">
    <img id="modalImg" src="" alt="PDBj Image">
  </a>

 <a id="rcsbLink" href="#" target="_blank">
  <img id="rcsbImg" src="" alt="RCSB Assembly" class="rcsb-image">
 </a>

  <div id="pdbeViews">
  <a id="pdbeLinkFront" href="#" target="_blank">
    <img id="pdbeFront" src="" alt="Front View">
  </a>
  <a id="pdbeLinkSide" href="#" target="_blank">
    <img id="pdbeSide" src="" alt="Side View">
  </a>
  <a id="pdbeLinkTop" href="#" target="_blank">
    <img id="pdbeTop" src="" alt="Top View">
  </a>
</div>

  <div class="modal-title" id="modalTitle"></div>
  <button class="nav-button next" onclick="nextImage()">&#10095;</button>
</div>

<script>
const entries = [
""" + image_data_js + """
];

let currentIndex = 0;

function openModal(index) {
    currentIndex = index;
    updateModal();
    document.getElementById("modal").style.display = "flex";
}

function updateModal() {
    const entry = entries[currentIndex];
    const pdbid = entry.id.toLowerCase();
    const pdbidUC = entry.id.toUpperCase();

    document.getElementById("modalImg").src = entry.src;
    document.getElementById("modalTitle").textContent = entry.title;
    document.getElementById("modalLink").href = entry.link;

    // RCSB image and link
    const rcsbURL = `https://cdn.rcsb.org/images/structures/${pdbid}_assembly-1.jpeg`;
    document.getElementById("rcsbImg").src = rcsbURL;
    document.getElementById("rcsbLink").href = `https://www.rcsb.org/structure/${pdbidUC}`;

    // PDBe views
    const pdbeURL = `https://www.ebi.ac.uk/pdbe/entry/pdb/${pdbid}`;
    document.getElementById("pdbeFront").src = `https://www.ebi.ac.uk/pdbe/static/entry/${pdbid}_assembly_1_chain_front_image-200x200.png`;
    document.getElementById("pdbeSide").src = `https://www.ebi.ac.uk/pdbe/static/entry/${pdbid}_assembly_1_chain_side_image-200x200.png`;
    document.getElementById("pdbeTop").src = `https://www.ebi.ac.uk/pdbe/static/entry/${pdbid}_assembly_1_chain_top_image-200x200.png`;

    document.getElementById("pdbeLinkFront").href = pdbeURL;
    document.getElementById("pdbeLinkSide").href = pdbeURL;
    document.getElementById("pdbeLinkTop").href = pdbeURL;
}


function closeModal() {
    document.getElementById("modal").style.display = "none";
}

function nextImage() {
    currentIndex = (currentIndex + 1) % entries.length;
    updateModal();
}

function prevImage() {
    currentIndex = (currentIndex - 1 + entries.length) % entries.length;
    updateModal();
}

document.addEventListener("keydown", function(event) {
    if (document.getElementById("modal").style.display === "flex") {
        if (event.key === "ArrowRight") nextImage();
        if (event.key === "ArrowLeft") prevImage();
        if (event.key === "Escape") closeModal();
    }
});
</script>

<div style="text-align:center; margin-top:20px;">
  Image data source: Protein Data Bank Japan (PDBj), licensed under CC-BY-4.0 International
</div>
<div style="text-align:center; margin-top:20px;">
  Image data source: RCSB PDB, CC0 1.0 Universal (CC0 1.0) Public Domain Dedication.
</div>
<div style="text-align:center; margin-top:20px;">
  Image data source: Protein Data Bank Europe (PDBe), licensed under CC BY 4.0 International
</div>
</body>
</html>"""

    with open("docs/index.html", "w") as output_file:
        output_file.write(html_content)

# Call the function with your .tsv file containing the entry names and descriptions
newEntryUrl="https://pdbj.org/rest/newweb/search/sql?q=select+bs.pdbid+from+pdbj.brief_summary+bs+inner+join+misc.id_meta_list+iml+on+bs.pdbid%3Diml.id+where+iml.category%3D%27pdb_new%27&format=txt"
entry_list=get_onlinetxt(newEntryUrl).split("\n")
output_file_name = "entries.tsv"
generate_tsv_from_entries(entry_list, output_file_name)
generate_html_from_tsv("entries.tsv")
