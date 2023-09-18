import requests
from bs4 import BeautifulSoup

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
    url = "https://data.pdbjbk1.pdbj.org/pdbjplus/data/pdb/mmjson-noatom/"+ pdbid + "-noatom.json"
    response = requests.get(url)
    name = "data_" + pdbid.upper()
    if response.status_code == 200:
        json_data = response.json()
        title=json_data[name]['struct']['title'][0]
        print(title)
        return title
    else:
        print(f"Failed to retrieve the JSON data. HTTP Status Code: {response.status_code}")
        return "error"

def generate_tsv_from_entries(entry_list, output_file_name):
    """Generate a .tsv file with entries and their respective descriptions."""
    with open(output_file_name, 'w') as file:
        for entry in entry_list:
            url = f"https://pdbj.org/mine/summary/{entry}"
            description = get_title(entry)
            if description:
                file.write(f"{entry}\t{description}\n")
            else:
                print(f"Warning: Could not fetch description for {entry}")

def generate_html_from_tsv(file_name):
    with open(file_name, 'r') as file:
        lines = [line.strip().split('\t') for line in file]
        entries = [(line[0], line[1]) for line in lines]

    # Start building the HTML content
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDBj Updates</title>
    <style>
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

    for entry, title in entries:
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

</body>
</html>
"""

    # Save the generated HTML to a file
    with open("./docs/index.html", "w") as output_file:
        output_file.write(html_content)

# Call the function with your .tsv file containing the entry names and descriptions
newEntryUrl="https://pdbj.org/rest/newweb/search/sql?q=select+bs.pdbid+from+pdbj.brief_summary+bs+inner+join+misc.id_meta_list+iml+on+bs.pdbid%3Diml.id+where+iml.category%3D%27pdb_new%27&format=txt"
entry_list=get_onlinetxt(newEntryUrl).split("\n")
output_file_name = "entries.tsv"
generate_tsv_from_entries(entry_list, output_file_name)
generate_html_from_tsv("entries.tsv")
