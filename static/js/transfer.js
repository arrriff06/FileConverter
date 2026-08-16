// Elements
const fileInput = document.getElementById("transferFileInput");
const uploadBox = document.getElementById("uploadBox");
const codeDisplay = document.getElementById("codeDisplay");
const codeInput = document.getElementById("codeInput");

// Allowed types
const ALLOWED_TYPES = [
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "video/mp4", "video/quicktime", "video/x-msvideo", "video/webm", "video/x-matroska",
    "application/pdf",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
];

// Track selected files across multiple picks
let selectedFiles = [];

// Preview container (already in HTML, just grab it)
const previewContainer = document.getElementById("transferPreview");

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
    addFiles(Array.from(e.dataTransfer.files));
});

// ---------- FILE SELECT ----------
fileInput.addEventListener("change", () => {
    addFiles(Array.from(fileInput.files));
    fileInput.value = ""; // reset so same file can be re-added
});

// ---------- ADD FILES (with validation) ----------
function addFiles(newFiles) {
    let rejectedCount = 0;

    newFiles.forEach(file => {
        const isAllowed = ALLOWED_TYPES.includes(file.type);

        if (!isAllowed) {
            rejectedCount++;
            return;
        }

        // Avoid duplicate file names
        const alreadyAdded = selectedFiles.some(f => f.name === file.name && f.size === file.size);
        if (!alreadyAdded) {
            selectedFiles.push(file);
        }
    });

    if (rejectedCount > 0) {
        alert(`${rejectedCount} file(s) were rejected. Only images, videos, PDF, PPT, and Word files are allowed.`);
    }

    renderPreviews();
}

// ---------- RENDER PREVIEWS ----------
function renderPreviews() {
    previewContainer.innerHTML = "";

    selectedFiles.forEach((file, index) => {
        const div = document.createElement("div");
        div.className = "transfer-file";

        // Pick icon based on type
        let icon = "📄";
        if (file.type.startsWith("image/")) icon = "🖼️";
        else if (file.type.startsWith("video/")) icon = "🎬";
        else if (file.type === "application/pdf") icon = "📕";
        else if (file.type.includes("powerpoint") || file.type.includes("presentation")) icon = "📊";
        else if (file.type.includes("word") || file.type.includes("document")) icon = "📝";

        div.innerHTML = `
            <span class="file-icon">${icon}</span>
            <span class="file-name" title="${file.name}">${file.name}</span>
            <span class="file-size">${(file.size / 1024).toFixed(1)} KB</span>
            <button class="remove-file" data-index="${index}" title="Remove">✕</button>
        `;

        div.querySelector(".remove-file").addEventListener("click", (e) => {
            const i = parseInt(e.target.getAttribute("data-index"));
            selectedFiles.splice(i, 1);
            renderPreviews();
        });

        previewContainer.appendChild(div);
    });

    // Show total count if more than 1 file
    if (selectedFiles.length > 1) {
        const total = document.createElement("p");
        total.className = "file-count";
        total.innerText = `${selectedFiles.length} files selected`;
        previewContainer.appendChild(total);
    }
}

// ---------- SEND FILE ----------
async function sendFile() {
    if (selectedFiles.length === 0) {
        alert("Please select at least one file first.");
        return;
    }

    codeDisplay.innerText = "Uploading...";

    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append("files", file);
    });

    try {
        const res = await fetch("/convert/transfer/send", {
            method: "POST",
            body: formData,
        });

        const data = await res.json();

        if (data.code) {
            codeDisplay.innerHTML = `
                <div class="code-box">
                    <span>Your Code:</span>
                    <strong>${data.code}</strong>
                    <button class="copy-btn" onclick="copyCode('${data.code}')">Copy</button>
                </div>
            `;
            // Clear files after successful send
            selectedFiles = [];
            renderPreviews();
        } else {
            codeDisplay.innerText = "Upload failed. Try again.";
        }

    } catch (err) {
        codeDisplay.innerText = "Upload failed. Check your connection.";
        console.error(err);
    }
}

// ---------- COPY CODE ----------
function copyCode(code) {
    navigator.clipboard.writeText(code).then(() => {
        alert("Code copied: " + code);
    });
}

// ---------- RECEIVE ----------
async function receiveFile() {
    const code = codeInput.value.trim().toUpperCase();

    if (!code) {
        alert("Please enter a code.");
        return;
    }

    // Check code validity first
    try {
        const res = await fetch(`/convert/transfer/check/${code}`);
        const data = await res.json();

        if (data.valid) {
            if (data.count > 1) {
                // Multiple files → download as zip
                window.location.href = `/convert/transfer/receive/${code}`;
            } else {
                window.location.href = `/convert/transfer/receive/${code}`;
            }
        } else {
            // Show error inline instead of just redirecting
            const receiveBox = document.querySelector(".box:last-child");
            let errMsg = receiveBox.querySelector(".receive-error");
            if (!errMsg) {
                errMsg = document.createElement("p");
                errMsg.className = "receive-error";
                receiveBox.appendChild(errMsg);
            }
            errMsg.innerText = "❌ Invalid or expired code. Please try again.";
        }
    } catch (err) {
        window.location.href = `/convert/transfer/receive/${code}`;
    }
}
