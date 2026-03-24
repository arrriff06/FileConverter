document.addEventListener("DOMContentLoaded", function () {

console.log("JS WORKING");

/* ============================= */
/* ELEMENTS */
/* ============================= */
const dropArea = document.getElementById("dropArea");
const fileInput = document.getElementById("fileInput");
const filePreview = document.getElementById("filePreview");
const form = document.getElementById("uploadForm");
const loader = document.getElementById("loader");
const clearBtn = document.getElementById("clearAllBtn");

// Dropdown elements (SAFE CHECK)
const selectBox = document.querySelector(".select-box");
const optionsContainer = document.querySelector(".options-container");
const options = document.querySelectorAll(".option");
const selected = document.querySelector(".selected");
const input = document.getElementById("conversionInput");

// Store selected files
let selectedFiles = [];


/* ============================= */
/* FILE UPLOAD SYSTEM */
/* ============================= */

// Click to upload
if (dropArea && fileInput) {
    dropArea.addEventListener("click", () => fileInput.click());

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
        selectedFiles = [...selectedFiles, ...droppedFiles];

        updatePreview();
    });
}

// File input change
if (fileInput) {
    fileInput.addEventListener("change", (e) => {
        const newFiles = Array.from(e.target.files);
        selectedFiles = [...selectedFiles, ...newFiles];
        updatePreview();
    });
}


/* ============================= */
/* PREVIEW FILE LIST */
/* ============================= */
function updatePreview() {

    if (!filePreview) return;

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

// Remove file
window.removeFile = function(index) {
    selectedFiles.splice(index, 1);
    updatePreview();
};

// Clear all
if (clearBtn) {
    clearBtn.addEventListener("click", () => {
        selectedFiles = [];
        updatePreview();
    });
}

// Sync files to input
function updateInputFiles() {
    const dt = new DataTransfer();
    selectedFiles.forEach(file => dt.items.add(file));
    fileInput.files = dt.files;
}


/* ============================= */
/* FORM SUBMIT */
/* ============================= */
if (form) {
    form.addEventListener("submit", function (e) {

        if (selectedFiles.length === 0) {
            e.preventDefault();
            alert("Please select at least one file");
            return;
        }

        if (loader) loader.style.display = "flex";

        const btn = form.querySelector("button");
        if (btn) {
            btn.innerText = "Converting...";
            btn.disabled = true;
        }

        e.preventDefault();
        setTimeout(() => form.submit(), 800);
    });
}


/* ============================= */
/* CUSTOM DROPDOWN */
/* ============================= */
if (selectBox && optionsContainer && selected && input) {

    selectBox.addEventListener("click", () => {
        selectBox.classList.toggle("active");
        optionsContainer.classList.toggle("active");
    });

    options.forEach(option => {
        option.addEventListener("click", () => {
            selected.innerText = option.innerText;
            input.value = option.getAttribute("data-value");

            selectBox.classList.remove("active");
            optionsContainer.classList.remove("active");
        });
    });

    document.addEventListener("click", (e) => {
        const wrapper = document.getElementById("customSelect");
        if (wrapper && !wrapper.contains(e.target)) {
            selectBox.classList.remove("active");
            optionsContainer.classList.remove("active");
        }
    });
}


/* ============================= */
/* IMAGE EDIT SYSTEM */
/* ============================= */

let currentImage = null;
let rotation = 0;
let scaleX = 1;
let isGrayscale = false;

// Select image
window.selectImage = function(img){

    document.querySelectorAll('.preview-gallery').forEach(el => {
        el.classList.remove('active');
    });

    img.classList.add('active');

    currentImage = img;

    rotation = 0;
    scaleX = 1;
    isGrayscale = false;

    applyStyles();
};

// Apply styles
function applyStyles(){
    if (!currentImage) return;

    currentImage.style.transform = `rotate(${rotation}deg) scaleX(${scaleX})`;
    currentImage.style.filter = isGrayscale ? "grayscale(100%)" : "none";
}

// Rotate
window.rotateImage = function(){
    if (!currentImage) return;
    rotation += 90;
    applyStyles();
};

// Flip
window.flipImage = function(){
    if (!currentImage) return;
    scaleX *= -1;
    applyStyles();
};

// Grayscale
window.grayscale = function(){
    if (!currentImage) return;
    isGrayscale = !isGrayscale;
    applyStyles();
};

// Reset
window.resetImage = function(){
    if (!currentImage) return;

    rotation = 0;
    scaleX = 1;
    isGrayscale = false;

    applyStyles();
};


/* ============================= */
/* AUTO SELECT FIRST IMAGE */
/* ============================= */
window.addEventListener("load", function () {

    const images = document.querySelectorAll(".preview-gallery");
    const tools = document.getElementById("editSection");

    if (images.length > 0) {

        currentImage = images[0];

        rotation = 0;
        scaleX = 1;
        isGrayscale = false;

        applyStyles();

        images[0].classList.add("active");

        if (tools){
            tools.style.display = "flex";
        }
    }
});

});
/* ============================= */
/* CROP FEATURE */
/* ============================= */

let cropper = null;

// Start crop
window.startCrop = function(){
    if (!currentImage) return;

    if (cropper) {
        cropper.destroy();
    }

    cropper = new Cropper(currentImage, {
        aspectRatio: NaN,
        viewMode: 1,
    });
};

// Apply crop
window.applyCrop = function(){
    if (!cropper) return;

    const canvas = cropper.getCroppedCanvas();

    // Replace image with cropped version
    currentImage.src = canvas.toDataURL("image/png");

    cropper.destroy();
    cropper = null;
};