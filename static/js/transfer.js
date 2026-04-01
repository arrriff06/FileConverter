// Elements
const fileInput = document.getElementById("transferFileInput");
const uploadBox = document.getElementById("uploadBox");
const codeDisplay = document.getElementById("codeDisplay");
const codeInput = document.getElementById("codeInput");

// create preview container dynamically
let previewContainer = document.createElement("div");
previewContainer.id = "transferPreview";
uploadBox.after(previewContainer);

// ---------- DRAG & DROP ----------
uploadBox.addEventListener("click", () => fileInput.click());

uploadBox.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadBox.classList.add("drag-active");
});

uploadBox.addEventListener("dragleave", () => {
    uploadBox.classList.remove("drag-active");
});

uploadBox.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadBox.classList.remove("drag-active");

    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        showPreview();
    }
});

// ---------- FILE SELECT ----------
fileInput.addEventListener("change", showPreview);

function showPreview() {
    previewContainer.innerHTML = "";

    const file = fileInput.files[0];
    if (!file) return;

    const div = document.createElement("div");
    div.className = "transfer-file";

    div.innerHTML = `
        <span>${file.name}</span>
        <button class="remove-file">X</button>
    `;

    div.querySelector("button").onclick = () => {
        fileInput.value = "";
        previewContainer.innerHTML = "";
    };

    previewContainer.appendChild(div);
}

// ---------- SEND FILE ----------
async function sendFile() {
    const file = fileInput.files[0];

    if (!file) {
        alert("Select file first");
        return;
    }

    codeDisplay.innerText = "Uploading...";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/convert/transfer/send", {
            method: "POST",
            body: formData,
        });

        const data = await res.json();
        codeDisplay.innerText = "Code: " + data.code;
    } catch (err) {
        codeDisplay.innerText = "Upload failed";
    }
}

// ---------- RECEIVE ----------
function receiveFile() {
    const code = codeInput.value.trim();

    if (!code) {
        alert("Enter code");
        return;
    }

    window.location.href = `/convert/transfer/receive/${code}`;
}