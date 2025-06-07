<!-- Modal Overlay -->
<div id="modal">
  <span class="close" onclick="closeModal()">&times;</span>
  <button class="nav-button prev" onclick="prevImage()">&#10094;</button>

  <div class="modal-images">
    <a id="modalLink" href="#" target="_blank">
      <img id="modalImg" src="" alt="PDBj Image">
    </a>

    <a id="rcsbLink" href="#" target="_blank">
      <img id="rcsbImg" src="" alt="RCSB Assembly" class="rcsb-image">
    </a>
  </div>

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
  <div id="modalIndex"></div>

  <button class="nav-button next" onclick="nextImage()">&#10095;</button>
</div>

<script>
const entries = [
{{IMAGE_DATA}}
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
  document.getElementById("modalIndex").textContent = `${currentIndex + 1} / ${entries.length}`;

  const rcsbURL = `https://cdn.rcsb.org/images/structures/${pdbid}_assembly-1.jpeg`;
  document.getElementById("rcsbImg").src = rcsbURL;
  document.getElementById("rcsbLink").href = `https://www.rcsb.org/structure/${pdbidUC}`;

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


