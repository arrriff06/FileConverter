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

let cropMode = false;
let startX, startY, endX, endY;

function startCrop() {
    if (!currentImage) return;

    cropMode = true;
    alert("Drag on image to crop");

    currentImage.style.cursor = "crosshair";

    currentImage.onmousedown = function(e) {
        startX = e.offsetX;
        startY = e.offsetY;
    };

    currentImage.onmouseup = function(e) {
        endX = e.offsetX;
        endY = e.offsetY;

        document.getElementById("cropSection").style.display = "flex";
    };
}

function applyCrop() {
    if (!currentImage) return;

    const canvas = document.getElementById("cropCanvas");
    const ctx = canvas.getContext("2d");

    const img = new Image();
    img.src = currentImage.src;

    img.onload = function() {

        const width = endX - startX;
        const height = endY - startY;

        canvas.width = width;
        canvas.height = height;

        ctx.drawImage(
            img,
            startX, startY, width, height,
            0, 0, width, height
        );

        currentImage.src = canvas.toDataURL("image/png");

        cropMode = false;
        currentImage.style.cursor = "default";
    };
}
/* =========================================================
   TEXT / CODE ROOM
   ========================================================= */

const roomTextInput = document.getElementById("roomTextInput");
const roomCharCount = document.getElementById("roomCharCount");
const createdRoomResult = document.getElementById("createdRoomResult");
const createdRoomCode = document.getElementById("createdRoomCode");
const joinRoomCode = document.getElementById("joinRoomCode");
const roomContent = document.getElementById("roomContent");
const sharedRoomText = document.getElementById("sharedRoomText");
const copyStatus = document.getElementById("copyStatus");


/* ---------- CHARACTER COUNT ---------- */

if (roomTextInput) {

    roomTextInput.addEventListener("input", () => {

        const count = roomTextInput.value.length;

        roomCharCount.textContent =
            `${count.toLocaleString()} characters`;

    });

}


/* ---------- CREATE ROOM ---------- */

async function createRoom() {

    const text = roomTextInput.value.trim();

    if (!text) {
        alert("Please paste or type some text or code first.");
        roomTextInput.focus();
        return;
    }

    const button = document.getElementById("createRoomBtn");

    button.disabled = true;
    button.textContent = "Creating Room...";

    try {

        const response = await fetch("/convert/room/create", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: text
            })

        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Unable to create room."
            );
        }

        createdRoomCode.textContent = data.code;

        createdRoomResult.classList.remove("hidden");

        // Automatically scroll slightly to the generated code
        createdRoomResult.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });

    } catch (error) {

        console.error(error);

        alert(error.message);

    } finally {

        button.disabled = false;
        button.textContent = "Create Room";

    }

}


/* ---------- JOIN ROOM ---------- */

async function joinRoom() {

    const code = joinRoomCode.value.trim().toUpperCase();

    if (!code) {
        alert("Please enter a room code.");
        joinRoomCode.focus();
        return;
    }

    if (code.length !== 6) {
        alert("Room code must contain 6 characters.");
        return;
    }

    const button = joinRoomCode
        .closest(".room-box")
        .querySelector(".room-primary-btn");

    button.disabled = true;
    button.textContent = "Joining...";

    try {

        const response = await fetch(
            `/convert/room/${encodeURIComponent(code)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error || "Room not found."
            );
        }

        sharedRoomText.textContent = data.text;

        roomContent.classList.remove("hidden");

        copyStatus.textContent = "";

        roomContent.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });

    } catch (error) {

        console.error(error);

        roomContent.classList.add("hidden");

        alert(error.message);

    } finally {

        button.disabled = false;
        button.textContent = "Join Room";

    }

}


/* ---------- COPY ROOM CODE ---------- */

async function copyRoomCode() {

    const code = createdRoomCode.textContent.trim();

    if (!code) return;

    try {

        await navigator.clipboard.writeText(code);

        const button =
            document.querySelector(".copy-code-btn");

        const oldText = button.textContent;

        button.textContent = "Copied!";

        setTimeout(() => {
            button.textContent = oldText;
        }, 1500);

    } catch (error) {

        console.error(error);

        alert("Unable to copy the room code.");

    }

}


/* ---------- COPY SHARED CONTENT ---------- */

async function copyRoomContent() {

    const text = sharedRoomText.textContent;

    if (!text) return;

    try {

        await navigator.clipboard.writeText(text);

        copyStatus.textContent =
            "✓ Copied to clipboard";

        setTimeout(() => {
            copyStatus.textContent = "";
        }, 2000);

    } catch (error) {

        console.error(error);

        copyStatus.textContent =
            "Unable to copy content.";

    }

}


/* ---------- ENTER KEY TO JOIN ---------- */

if (joinRoomCode) {

    joinRoomCode.addEventListener("keydown", (event) => {

        if (event.key === "Enter") {
            joinRoom();
        }

    });

}