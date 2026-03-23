document.addEventListener("DOMContentLoaded", function () {

console.log("JS WORKING");

// Elements
const dropArea = document.getElementById("dropArea");
const fileInput = document.getElementById("fileInput");
const filePreview = document.getElementById("filePreview");
const form = document.getElementById("uploadForm");
const loader = document.getElementById("loader");
const clearBtn = document.getElementById("clearAllBtn");

// Store selected files manually
let selectedFiles = [];


/* ============================= */
/* CLICK TO OPEN FILE */
/* ============================= */
dropArea.addEventListener("click", () => {
    fileInput.click();
});


/* ============================= */
/* DRAG EVENTS */
/* ============================= */
dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("drag-active");
});

dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("drag-active");
});

dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove("drag-active");

    const droppedFiles = Array.from(e.dataTransfer.files);

    // ADD files instead of replacing
    selectedFiles = [...selectedFiles, ...droppedFiles];

    updatePreview();
});


/* ============================= */
/* FILE SELECT */
/* ============================= */
fileInput.addEventListener("change", (e) => {

    const newFiles = Array.from(e.target.files);

    // Append files
    selectedFiles = [...selectedFiles, ...newFiles];

    updatePreview();
});


/* ============================= */
/* UPDATE PREVIEW */
/* ============================= */
function updatePreview() {

    filePreview.innerHTML = "";

    if (selectedFiles.length === 0) {
        filePreview.innerHTML = "<p>No files selected</p>";
        return;
    }

    selectedFiles.forEach((file, index) => {

        const box = document.createElement("div");
        box.className = "file-box";

        box.innerHTML = `
            <span>📄 ${file.name}</span>
            <button onclick="removeFile(${index})">❌</button>
        `;

        filePreview.appendChild(box);
    });

    updateInputFiles();
}


/* ============================= */
/* REMOVE SINGLE FILE */
/* ============================= */
window.removeFile = function(index) {
    selectedFiles.splice(index, 1);
    updatePreview();
};


/* ============================= */
/* CLEAR ALL FILES */
/* ============================= */
if (clearBtn) {
    clearBtn.addEventListener("click", () => {
        selectedFiles = [];
        updatePreview();
    });
}


/* ============================= */
/* SYNC INPUT FILES (IMPORTANT) */
/* ============================= */
function updateInputFiles() {

    const dt = new DataTransfer();

    selectedFiles.forEach(file => {
        dt.items.add(file);
    });

    fileInput.files = dt.files;
}


/* ============================= */
/* FORM SUBMIT + LOADER */
/* ============================= */
form.addEventListener("submit", function (e) {

    if (selectedFiles.length === 0) {
        e.preventDefault();
        alert("Please select at least one file");
        return;
    }

    // SHOW LOADER
    loader.style.display = "flex";

    // Disable button
    const btn = form.querySelector("button");
    btn.innerText = "Converting...";
    btn.disabled = true;

    // DELAY SUBMIT (for smooth UX)
    e.preventDefault();

    setTimeout(() => {
        form.submit();
    }, 800);
});

});