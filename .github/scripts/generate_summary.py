import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_onlinetxt(url):
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        content = response.text
        return content
    else:
        print(f"Failed to retrieve the file. HTTP Status Code: {response.status_code}")
        return 0

def get_title(pdbid):
    url = "https://data.pdbj.org/pdbjplus/data/pdb/mmjson-noatom/" + pdbid + "-noatom.json"
    cwd = os.getcwd()
    cert_path = cwd + "/.ssl/" + "pdbj202407.cert"    
    #https://data.pdbj.org/pdbjplus/data/pdb/mmjson-noatom/9bgp-noatom.json
    # probably changed around the head of 2024 July
    #url = "https://data.pdbjbk1.pdbj.org/pdbjplus/data/pdb/mmjson-noatom/"+ pdbid + "-noatom.json"
    #response = requests.get(url,verify=False) # temporary workaround
    response = requests.get(url,verify=cert_path) # temporary workaround 
    name = "data_" + pdbid.upper()
    if response.status_code == 200:
        json_data = response.json()
        title=json_data[name]['struct']['title'][0]
        if "pdbx_contact_author" in json_data[name]:
            email = json_data[name]["pdbx_contact_author"]['email'][0]
        else:
            email = "zzzzzzz"
        print(title)
        return pdbid+":"+title, email
    else:
        print(f"Failed to retrieve the JSON data. HTTP Status Code: {response.status_code}")
        return "error"

def generate_tsv_from_entries(entry_list, output_file_name):
    """Generate a .tsv file with entries and their respective descriptions."""
    with open(output_file_name, 'w') as file:
        count = 0
        length = len(entry_list)
        for entry in entry_list:
            time.sleep(2) # sleep 2 seconds
            count += 1            
            print(entry + "  No. " + str(count) + " out of " + str(length) + " entries.")
            output = get_title(entry)
            print(output)            
            if len(output) == 2:
                email = output[1]
                description = output[0]
                if description and email:
                    file.write(f"{entry}\t{description}\t{email}\n")
                else:
                    print(f"Warning: Could not fetch description for {entry}")
            else:
                print(f"email or description is missing in  {entry}")

                


def generate_html_from_tsv(file_name):
    with open(file_name, 'r') as file:
        lines = [line.strip().split('\t') for line in file]
        entries = [(line[0], line[1], line[2]) for line in lines]

    entries = sorted(entries, key=lambda x: x[2])
    # Start building the HTML content
    # Get the current date and time
    now = datetime.now()    
    # Print the current date and time
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDBj Updates</title>"""

    html_content += """<div style="text-align:center;">""" + "Updated at " + str(now) + "</div> </body></html>"

    html_content +="""<style>
        .thumbnail-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 16px;
            padding: 20px;
        }

        img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            transition: transform 0.2s;
        }

        img:hover {
            transform: scale(1.1);
        }

        .entry-title {
            text-align: center;
            font-size: 14px;
            margin-top: 8px;
        }
    </style>
</head>
<body>

<div class="thumbnail-grid">
"""

    for entry, title, _ in entries:
        thumbnail_url = f"https://pdbj.org/molmil-images/mine/{entry}.png"
        entry_url = f"https://pdbj.org/mine/summary/{entry}"
        html_content += f'''
        <a href="{entry_url}" target="_blank">
            <img src="{thumbnail_url}" alt="Thumbnail for {entry}">
            <div class="entry-title">{title}</div>
        </a>
        '''

    html_content += """
</div>
<div style="text-align:center;">© Protein Data Bank Japan (PDBj) licensed under CC-BY-4.0 International</div></html>
"""
    
    # Save the generated HTML to a file
    with open("docs/index.html", "w") as output_file:
        output_file.write(html_content)

# Call the function with your .tsv file containing the entry names and descriptions
newEntryUrl="https://pdbj.org/rest/newweb/search/sql?q=select+bs.pdbid+from+pdbj.brief_summary+bs+inner+join+misc.id_meta_list+iml+on+bs.pdbid%3Diml.id+where+iml.category%3D%27pdb_new%27&format=txt"
entry_list=get_onlinetxt(newEntryUrl).split("\n")
output_file_name = "entries.tsv"
generate_tsv_from_entries(entry_list, output_file_name)
generate_html_from_tsv("entries.tsv")
