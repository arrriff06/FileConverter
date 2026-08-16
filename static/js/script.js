document.addEventListener("DOMContentLoaded", function () {

    console.log("FileConverter JS WORKING");


    /* =========================================================
       MAIN FILE CONVERTER
       ========================================================= */

    const dropArea =
        document.getElementById("dropArea");

    const fileInput =
        document.getElementById("fileInput");

    const filePreview =
        document.getElementById("filePreview");

    const form =
        document.getElementById("uploadForm");

    const loader =
        document.getElementById("loader");

    const clearBtn =
        document.getElementById("clearAllBtn");

    const convertBtn =
        document.getElementById("convertBtn");


    let selectedFiles = [];


    /* =========================================================
       FILE UPLOAD
       ========================================================= */

    if (dropArea && fileInput) {

        dropArea.addEventListener("click", function () {

            fileInput.click();

        });


        dropArea.addEventListener("dragover", function (event) {

            event.preventDefault();

            dropArea.classList.add("drag-active");

        });


        dropArea.addEventListener("dragleave", function () {

            dropArea.classList.remove("drag-active");

        });


        dropArea.addEventListener("drop", function (event) {

            event.preventDefault();

            dropArea.classList.remove("drag-active");

            const files =
                Array.from(event.dataTransfer.files);

            addMainFiles(files);

        });


        fileInput.addEventListener("change", function (event) {

            const files =
                Array.from(event.target.files);

            addMainFiles(files);

        });

    }


    /* =========================================================
       ADD MAIN CONVERTER FILES
       ========================================================= */

    function addMainFiles(files) {

        files.forEach(function (file) {

            const exists =
                selectedFiles.some(function (existing) {

                    return (
                        existing.name === file.name &&
                        existing.size === file.size &&
                        existing.lastModified === file.lastModified
                    );

                });


            if (!exists) {

                selectedFiles.push(file);

            }

        });


        updatePreview();

    }


    /* =========================================================
       MAIN FILE PREVIEW
       ========================================================= */

    function updatePreview() {

        if (!filePreview) {
            return;
        }


        filePreview.innerHTML = "";


        if (selectedFiles.length === 0) {

            filePreview.innerHTML =
                "<p>No files selected</p>";

            updateInputFiles();

            return;

        }


        selectedFiles.forEach(function (file, index) {

            const box =
                document.createElement("div");

            box.className = "file-box";


            const name =
                document.createElement("span");

            name.textContent =
                `📄 ${file.name}`;

            name.title =
                file.name;


            const remove =
                document.createElement("button");

            remove.type = "button";

            remove.textContent = "❌";

            remove.title = "Remove file";


            remove.addEventListener("click", function (event) {

                event.preventDefault();

                event.stopPropagation();

                selectedFiles.splice(index, 1);

                updatePreview();

            });


            box.appendChild(name);

            box.appendChild(remove);

            filePreview.appendChild(box);

        });


        updateInputFiles();

    }


    /* =========================================================
       SYNC INPUT FILES
       ========================================================= */

    function updateInputFiles() {

        if (!fileInput) {
            return;
        }


        try {

            const dataTransfer =
                new DataTransfer();


            selectedFiles.forEach(function (file) {

                dataTransfer.items.add(file);

            });


            fileInput.files =
                dataTransfer.files;

        } catch (error) {

            console.error(
                "FILE INPUT SYNC ERROR:",
                error
            );

        }

    }


    /* =========================================================
       CLEAR ALL
       ========================================================= */

    if (clearBtn) {

        clearBtn.addEventListener("click", function () {

            selectedFiles = [];


            if (fileInput) {

                fileInput.value = "";

            }


            updatePreview();

        });

    }


    /* =========================================================
       CONVERSION DROPDOWN
       ========================================================= */

    const customSelect =
        document.getElementById("customSelect");

    const selectBox =
        customSelect
            ? customSelect.querySelector(".select-box")
            : null;

    const optionsContainer =
        customSelect
            ? customSelect.querySelector(".options-container")
            : null;

    const options =
        customSelect
            ? customSelect.querySelectorAll(".option")
            : [];

    const selected =
        customSelect
            ? customSelect.querySelector(".selected")
            : null;

    const conversionInput =
        document.getElementById("conversionInput");


    if (
        selectBox &&
        optionsContainer &&
        selected &&
        conversionInput
    ) {

        selectBox.addEventListener("click", function (event) {

            event.stopPropagation();

            selectBox.classList.toggle("active");

            optionsContainer.classList.toggle("active");

        });


        options.forEach(function (option) {

            option.addEventListener("click", function (event) {

                event.stopPropagation();


                selected.textContent =
                    option.textContent.trim();


                conversionInput.value =
                    option.dataset.value || "";


                selectBox.classList.remove("active");

                optionsContainer.classList.remove("active");

            });

        });


        document.addEventListener("click", function (event) {

            if (
                customSelect &&
                !customSelect.contains(event.target)
            ) {

                selectBox.classList.remove("active");

                optionsContainer.classList.remove("active");

            }

        });

    }


    /* =========================================================
       MAIN FORM SUBMIT
       ========================================================= */

    if (form) {

        form.addEventListener("submit", function (event) {

            if (selectedFiles.length === 0) {

                event.preventDefault();

                alert(
                    "Please select at least one file."
                );

                return;

            }


            if (
                conversionInput &&
                !conversionInput.value
            ) {

                event.preventDefault();

                alert(
                    "Please select a conversion type."
                );

                return;

            }


            /*
             * Make absolutely sure the current
             * selected files are attached to
             * the form input.
             */

            updateInputFiles();


            if (loader) {

                loader.style.display = "flex";

            }


            if (convertBtn) {

                convertBtn.textContent =
                    "Converting...";

                convertBtn.disabled = true;

            }

        });

    }


    /* =========================================================
       FILE TRANSFER SYSTEM
       ========================================================= */

    console.log("FILE TRANSFER JS STARTED");


    const transferFileInput =
        document.getElementById("transferFileInput");

    const uploadBox =
        document.getElementById("uploadBox");

    const codeDisplay =
        document.getElementById("codeDisplay");

    const codeInput =
        document.getElementById("codeInput");

    const transferPreview =
        document.getElementById("transferPreview");


    let transferSelectedFiles = [];


    const ALLOWED_TRANSFER_TYPES = [

        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",

        "video/mp4",
        "video/quicktime",
        "video/x-msvideo",
        "video/webm",
        "video/x-matroska",

        "application/pdf",

        "application/vnd.ms-powerpoint",

        "application/vnd.openxmlformats-officedocument.presentationml.presentation",

        "application/msword",

        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    ];


    /*
     * MIME type can occasionally be empty depending
     * on browser/device, so also check extension.
     */

    const ALLOWED_TRANSFER_EXTENSIONS = [
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
        "pdf",
        "ppt",
        "pptx",
        "doc",
        "docx",
        "mp4",
        "mov",
        "avi",
        "mkv",
        "webm"
    ];


    function isTransferFileAllowed(file) {

        const extension =
            file.name
                .split(".")
                .pop()
                .toLowerCase();


        return (
            ALLOWED_TRANSFER_TYPES.includes(file.type) ||
            ALLOWED_TRANSFER_EXTENSIONS.includes(extension)
        );

    }


    /* =========================================================
       TRANSFER UPLOAD BOX
       ========================================================= */

    if (uploadBox && transferFileInput) {

        uploadBox.addEventListener("click", function () {

            transferFileInput.click();

        });


        uploadBox.addEventListener("dragover", function (event) {

            event.preventDefault();

            uploadBox.classList.add("drag-active");

        });


        uploadBox.addEventListener("dragleave", function () {

            uploadBox.classList.remove("drag-active");

        });


        uploadBox.addEventListener("drop", function (event) {

            event.preventDefault();

            uploadBox.classList.remove("drag-active");


            const files =
                Array.from(event.dataTransfer.files);


            addTransferFiles(files);

        });


        transferFileInput.addEventListener("change", function () {

            const files =
                Array.from(transferFileInput.files);


            addTransferFiles(files);


            /*
             * Allows selecting the same file again.
             */

            transferFileInput.value = "";

        });

    }


    /* =========================================================
       ADD TRANSFER FILES
       ========================================================= */

    function addTransferFiles(files) {

        let rejectedCount = 0;


        files.forEach(function (file) {

            if (!isTransferFileAllowed(file)) {

                rejectedCount++;

                return;

            }


            const duplicate =
                transferSelectedFiles.some(function (existingFile) {

                    return (
                        existingFile.name === file.name &&
                        existingFile.size === file.size &&
                        existingFile.lastModified === file.lastModified
                    );

                });


            if (!duplicate) {

                transferSelectedFiles.push(file);

            }

        });


        if (rejectedCount > 0) {

            alert(
                `${rejectedCount} file(s) were rejected.\n\n` +
                "Allowed: images, videos, PDF, PPT, and Word files."
            );

        }


        renderTransferPreviews();

    }


    /* =========================================================
       TRANSFER FILE ICON
       ========================================================= */

    function getTransferFileIcon(file) {

        const extension =
            file.name
                .split(".")
                .pop()
                .toLowerCase();


        if (file.type.startsWith("image/")) {
            return "🖼️";
        }


        if (
            file.type.startsWith("video/") ||
            [
                "mp4",
                "mov",
                "avi",
                "mkv",
                "webm"
            ].includes(extension)
        ) {

            return "🎬";

        }


        if (extension === "pdf") {
            return "📕";
        }


        if (
            ["ppt", "pptx"].includes(extension)
        ) {

            return "📊";

        }


        if (
            ["doc", "docx"].includes(extension)
        ) {

            return "📝";

        }


        return "📄";

    }


    /* =========================================================
       FILE SIZE
       ========================================================= */

    function formatTransferFileSize(bytes) {

        if (bytes < 1024) {

            return `${bytes} B`;

        }


        if (bytes < 1024 * 1024) {

            return (
                `${(bytes / 1024).toFixed(1)} KB`
            );

        }


        if (bytes < 1024 * 1024 * 1024) {

            return (
                `${(bytes / (1024 * 1024)).toFixed(1)} MB`
            );

        }


        return (
            `${(
                bytes /
                (1024 * 1024 * 1024)
            ).toFixed(1)} GB`
        );

    }


    /* =========================================================
       RENDER TRANSFER PREVIEW
       ========================================================= */

    function renderTransferPreviews() {

        if (!transferPreview) {
            return;
        }


        transferPreview.innerHTML = "";


        transferSelectedFiles.forEach(function (file, index) {

            const fileBox =
                document.createElement("div");

            fileBox.className =
                "transfer-file";


            const icon =
                document.createElement("span");

            icon.className =
                "file-icon";

            icon.textContent =
                getTransferFileIcon(file);


            const name =
                document.createElement("span");

            name.className =
                "file-name";

            name.textContent =
                file.name;

            name.title =
                file.name;


            const size =
                document.createElement("span");

            size.className =
                "file-size";

            size.textContent =
                formatTransferFileSize(file.size);


            const removeButton =
                document.createElement("button");

            removeButton.type =
                "button";

            removeButton.className =
                "remove-file";

            removeButton.textContent =
                "✕";

            removeButton.title =
                "Remove file";


            removeButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    event.stopPropagation();


                    transferSelectedFiles.splice(
                        index,
                        1
                    );


                    renderTransferPreviews();

                }
            );


            fileBox.appendChild(icon);

            fileBox.appendChild(name);

            fileBox.appendChild(size);

            fileBox.appendChild(removeButton);


            transferPreview.appendChild(fileBox);

        });


        if (transferSelectedFiles.length > 1) {

            const total =
                document.createElement("p");

            total.className =
                "file-count";

            total.textContent =
                `${transferSelectedFiles.length} files selected`;


            transferPreview.appendChild(total);

        }

    }


    /* =========================================================
       SEND FILE
       ========================================================= */

    window.sendFile = async function () {

        if (transferSelectedFiles.length === 0) {

            alert(
                "Please select at least one file first."
            );

            return;

        }


        if (codeDisplay) {

            codeDisplay.textContent =
                "Uploading...";

        }


        const formData =
            new FormData();


        transferSelectedFiles.forEach(function (file) {

            formData.append(
                "files",
                file
            );

        });


        try {

            const response =
                await fetch(
                    "/convert/transfer/send",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            if (
                !response.ok ||
                !data.code
            ) {

                throw new Error(
                    data.error ||
                    "Upload failed."
                );

            }


            displayTransferCode(data.code);


            transferSelectedFiles = [];

            renderTransferPreviews();


        } catch (error) {

            console.error(
                "SEND FILE ERROR:",
                error
            );


            if (codeDisplay) {

                codeDisplay.textContent =
                    error.message ||
                    "Upload failed. Check your connection.";

            }

        }

    };


    /* =========================================================
       DISPLAY TRANSFER CODE
       ========================================================= */

    function displayTransferCode(code) {

        if (!codeDisplay) {
            return;
        }


        codeDisplay.innerHTML = "";


        const codeBox =
            document.createElement("div");

        codeBox.className =
            "code-box";


        const label =
            document.createElement("span");

        label.textContent =
            "Your Code:";


        const codeElement =
            document.createElement("strong");

        codeElement.textContent =
            code;


        const copyButton =
            document.createElement("button");

        copyButton.type =
            "button";

        copyButton.className =
            "transfer-copy-btn";

        copyButton.textContent =
            "Copy";


        copyButton.addEventListener(
            "click",
            function () {

                copyText(
                    code,
                    copyButton,
                    "Copy"
                );

            }
        );


        codeBox.appendChild(label);

        codeBox.appendChild(codeElement);

        codeBox.appendChild(copyButton);


        codeDisplay.appendChild(codeBox);

    }


    /* =========================================================
       RECEIVE FILE
       ========================================================= */

    window.receiveFile = async function () {

        if (!codeInput) {
            return;
        }


        const code =
            codeInput.value
                .trim()
                .toUpperCase();


        if (!code) {

            alert(
                "Please enter a code."
            );

            codeInput.focus();

            return;

        }


        if (code.length !== 6) {

            alert(
                "Please enter a valid 6-character code."
            );

            codeInput.focus();

            return;

        }


        try {

            const response =
                await fetch(
                    `/convert/transfer/check/${encodeURIComponent(code)}`
                );


            const data =
                await response.json();


            if (
                !response.ok ||
                !data.valid
            ) {

                throw new Error(
                    "Invalid or expired code."
                );

            }


            /*
             * Flask sends the actual file here.
             */

            window.location.href =
                `/convert/transfer/receive/${encodeURIComponent(code)}`;


        } catch (error) {

            console.error(
                "RECEIVE FILE ERROR:",
                error
            );


            alert(
                error.message ||
                "Invalid or expired code."
            );

        }

    };


    /* =========================================================
       ENTER KEY FOR TRANSFER CODE
       ========================================================= */

    if (codeInput) {

        codeInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    window.receiveFile();

                }

            }
        );

    }


    /* =========================================================
       TEXT & CODE ROOM
       ========================================================= */

    console.log("TEXT & CODE ROOM JS STARTED");


    const pasteContent =
        document.getElementById("pasteContent");

    const pasteCharacterCount =
        document.getElementById("pasteCharacterCount");

    const generateCodeBtn =
        document.getElementById("generateCodeBtn");

    const generatedCodeSection =
        document.getElementById("generatedCodeSection");

    const generatedRoomCode =
        document.getElementById("generatedRoomCode");

    const copyGeneratedCodeBtn =
        document.getElementById("copyGeneratedCodeBtn");

    const generateStatus =
        document.getElementById("generateStatus");

    const joinCode =
        document.getElementById("joinCode");

    const joinRoomBtn =
        document.getElementById("joinRoomBtn");

    const sharedContentSection =
        document.getElementById("sharedContentSection");

    const roomCode =
        document.getElementById("roomCode");

    const copyRoomCodeBtn =
        document.getElementById("copyRoomCodeBtn");

    const copyContentBtn =
        document.getElementById("copyContentBtn");

    const roomContent =
        document.getElementById("roomContent");

    const characterCount =
        document.getElementById("characterCount");

    const saveStatus =
        document.getElementById("saveStatus");

    const roomStatus =
        document.getElementById("roomStatus");

    const leaveRoomBtn =
        document.getElementById("leaveRoomBtn");


    let currentRoomCode = null;

    let pollingTimer = null;

    let saveTimer = null;

    let isSaving = false;


    /* =========================================================
       PASTE CHARACTER COUNT
       ========================================================= */

    function updatePasteCharacterCount() {

        if (
            !pasteContent ||
            !pasteCharacterCount
        ) {

            return;

        }


        const count =
            pasteContent.value.length;


        pasteCharacterCount.textContent =
            `${count} character${count === 1 ? "" : "s"}`;

    }


    if (pasteContent) {

        pasteContent.addEventListener(
            "input",
            updatePasteCharacterCount
        );

    }


    /* =========================================================
       CREATE ROOM FROM PASTE
       ========================================================= */

    if (generateCodeBtn) {

        generateCodeBtn.addEventListener(
            "click",
            async function () {

                const content =
                    pasteContent
                        ? pasteContent.value
                        : "";


                if (!content.trim()) {

                    alert(
                        "Please paste something first."
                    );

                    if (pasteContent) {
                        pasteContent.focus();
                    }

                    return;

                }


                generateCodeBtn.disabled = true;

                generateCodeBtn.textContent =
                    "Generating...";


                if (generateStatus) {

                    generateStatus.textContent =
                        "Creating room...";

                }


                try {

                    const response =
                        await fetch(
                            "/convert/room/create",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    content: content,
                                    type: "text"
                                })
                            }
                        );


                    const data =
                        await response.json();


                    if (
                        !response.ok ||
                        !data.code
                    ) {

                        throw new Error(
                            data.error ||
                            "Unable to generate code."
                        );

                    }


                    currentRoomCode =
                        data.code
                            .toUpperCase();


                    if (generatedRoomCode) {

                        generatedRoomCode.textContent =
                            currentRoomCode;

                    }


                    if (generatedCodeSection) {

                        generatedCodeSection.style.display =
                            "block";

                    }


                    if (generateStatus) {

                        generateStatus.textContent =
                            "Code generated successfully";

                    }


                } catch (error) {

                    console.error(
                        "GENERATE ROOM ERROR:",
                        error
                    );


                    if (generateStatus) {

                        generateStatus.textContent =
                            "Failed to generate code";

                    }


                    alert(
                        error.message ||
                        "Unable to generate code."
                    );

                } finally {

                    generateCodeBtn.disabled =
                        false;

                    generateCodeBtn.textContent =
                        "Generate Code";

                }

            }
        );

    }


    /* =========================================================
       JOIN ROOM
       ========================================================= */

    if (joinRoomBtn) {

        joinRoomBtn.addEventListener(
            "click",
            async function () {

                const code =
                    joinCode
                        ? joinCode.value
                            .trim()
                            .toUpperCase()
                        : "";


                if (!code) {

                    alert(
                        "Please enter a room code."
                    );

                    if (joinCode) {
                        joinCode.focus();
                    }

                    return;

                }


                if (code.length !== 6) {

                    alert(
                        "Please enter a valid 6-character room code."
                    );

                    if (joinCode) {
                        joinCode.focus();
                    }

                    return;

                }


                joinRoomBtn.disabled = true;

                joinRoomBtn.textContent =
                    "Opening...";


                try {

                    /*
                     * IMPORTANT:
                     *
                     * Flask route:
                     * GET /room/<code>
                     *
                     * Therefore:
                     * /convert/room/ABC123
                     */

                    const response =
                        await fetch(
                            `/convert/room/${encodeURIComponent(code)}`
                        );


                    const data =
                        await response.json();


                    if (
                        !response.ok ||
                        !data.success
                    ) {

                        throw new Error(
                            data.error ||
                            "Room not found."
                        );

                    }


                    openSharedRoom(
                        code,
                        data.content || ""
                    );


                } catch (error) {

                    console.error(
                        "JOIN ROOM ERROR:",
                        error
                    );


                    alert(
                        error.message ||
                        "Room not found or expired."
                    );

                } finally {

                    joinRoomBtn.disabled =
                        false;

                    joinRoomBtn.textContent =
                        "Open";

                }

            }
        );

    }


    /* =========================================================
       ENTER KEY FOR ROOM CODE
       ========================================================= */

    if (joinCode && joinRoomBtn) {

        joinCode.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Enter") {

                    event.preventDefault();

                    joinRoomBtn.click();

                }

            }
        );

    }


    /* =========================================================
       OPEN SHARED ROOM
       ========================================================= */

    function openSharedRoom(code, content) {

        currentRoomCode =
            code.toUpperCase();


        if (roomCode) {

            roomCode.textContent =
                currentRoomCode;

        }


        if (roomContent) {

            roomContent.value =
                content || "";

        }


        if (sharedContentSection) {

            sharedContentSection.style.display =
                "block";

        }


        updateCharacterCount();


        if (roomStatus) {

            roomStatus.textContent =
                "Connected";

        }


        if (saveStatus) {

            saveStatus.textContent =
                "Ready";

        }


        startRoomPolling();


        console.log(
            "ROOM OPENED:",
            currentRoomCode
        );

    }


    /* =========================================================
       CHARACTER COUNT
       ========================================================= */

    function updateCharacterCount() {

        if (
            !roomContent ||
            !characterCount
        ) {

            return;

        }


        const count =
            roomContent.value.length;


        characterCount.textContent =
            `${count} character${count === 1 ? "" : "s"}`;

    }


    if (roomContent) {

        roomContent.addEventListener(
            "input",
            function () {

                updateCharacterCount();

                scheduleRoomSave();

            }
        );

    }


    /* =========================================================
       SCHEDULE ROOM SAVE
       ========================================================= */

    function scheduleRoomSave() {

        if (!currentRoomCode) {
            return;
        }


        if (saveTimer) {

            clearTimeout(saveTimer);

        }


        if (saveStatus) {

            saveStatus.textContent =
                "Saving...";

        }


        saveTimer =
            setTimeout(
                function () {

                    saveRoomContent();

                },
                500
            );

    }


    /* =========================================================
       SAVE ROOM
       ========================================================= */

    async function saveRoomContent() {

        if (
            !currentRoomCode ||
            !roomContent
        ) {

            return;

        }


        if (isSaving) {
            return;
        }


        isSaving = true;


        const content =
            roomContent.value;


        try {

            /*
             * IMPORTANT:
             *
             * Flask route:
             * POST /room/<code>/update
             *
             * Therefore:
             * /convert/room/ABC123/update
             */

            const response =
                await fetch(
                    `/convert/room/${encodeURIComponent(currentRoomCode)}/update`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            content: content,
                            type: "text"
                        })
                    }
                );


            const data =
                await response.json();


            if (
                !response.ok ||
                !data.success
            ) {

                throw new Error(
                    data.error ||
                    "Unable to save content."
                );

            }


            if (saveStatus) {

                saveStatus.textContent =
                    "Saved";

            }

        } catch (error) {

            console.error(
                "SAVE ROOM ERROR:",
                error
            );


            if (saveStatus) {

                saveStatus.textContent =
                    "Save failed";

            }

        } finally {

            isSaving = false;

        }

    }


    /* =========================================================
       ROOM POLLING
       ========================================================= */

    function startRoomPolling() {

        stopRoomPolling();


        /*
         * Load immediately.
         */

        loadRoomContent();


        /*
         * Then synchronize every second.
         */

        pollingTimer =
            setInterval(
                loadRoomContent,
                1000
            );

    }


    async function loadRoomContent() {

        if (!currentRoomCode) {
            return;
        }


        /*
         * Do not overwrite the editor while
         * a local save is in progress.
         */

        if (isSaving) {
            return;
        }


        try {

            /*
             * IMPORTANT:
             *
             * Flask:
             * GET /room/<code>
             */

            const response =
                await fetch(
                    `/convert/room/${encodeURIComponent(currentRoomCode)}`,
                    {
                        method: "GET",
                        cache: "no-store"
                    }
                );


            if (!response.ok) {

                if (response.status === 404) {

                    if (roomStatus) {

                        roomStatus.textContent =
                            "Room expired";

                    }

                    stopRoomPolling();

                }

                return;

            }


            const data =
                await response.json();


            if (!data.success) {
                return;
            }


            const serverContent =
                data.content || "";


            /*
             * Only update if the server has
             * different content.
             */

            if (
                roomContent &&
                serverContent !== roomContent.value
            ) {

                const cursorStart =
                    roomContent.selectionStart;

                const cursorEnd =
                    roomContent.selectionEnd;


                roomContent.value =
                    serverContent;


                updateCharacterCount();


                /*
                 * Restore cursor if possible.
                 */

                try {

                    roomContent.setSelectionRange(
                        Math.min(
                            cursorStart,
                            serverContent.length
                        ),
                        Math.min(
                            cursorEnd,
                            serverContent.length
                        )
                    );

                } catch (error) {

                    // Ignore cursor restore errors

                }

            }


            if (roomStatus) {

                roomStatus.textContent =
                    "Connected";

            }

        } catch (error) {

            console.error(
                "ROOM SYNC ERROR:",
                error
            );


            if (roomStatus) {

                roomStatus.textContent =
                    "Connection problem";

            }

        }

    }


    /* =========================================================
       STOP ROOM POLLING
       ========================================================= */

    function stopRoomPolling() {

        if (pollingTimer) {

            clearInterval(
                pollingTimer
            );

            pollingTimer = null;

        }

    }


    /* =========================================================
       COPY GENERATED ROOM CODE
       ========================================================= */

    if (copyGeneratedCodeBtn) {

        copyGeneratedCodeBtn.addEventListener(
            "click",
            function () {

                const code =
                    generatedRoomCode
                        ? generatedRoomCode.textContent.trim()
                        : "";


                if (
                    !code ||
                    code === "------"
                ) {

                    return;

                }


                copyText(
                    code,
                    copyGeneratedCodeBtn,
                    "Copy"
                );

            }
        );

    }


    /* =========================================================
       COPY ROOM CODE
       ========================================================= */

    if (copyRoomCodeBtn) {

        copyRoomCodeBtn.addEventListener(
            "click",
            function () {

                if (!currentRoomCode) {
                    return;
                }


                copyText(
                    currentRoomCode,
                    copyRoomCodeBtn,
                    "Copy"
                );

            }
        );

    }


    /* =========================================================
       COPY ROOM CONTENT
       ========================================================= */

    if (copyContentBtn) {

        copyContentBtn.addEventListener(
            "click",
            function () {

                if (!roomContent) {
                    return;
                }


                const content =
                    roomContent.value;


                if (!content) {

                    alert(
                        "There is no content to copy."
                    );

                    return;

                }


                copyText(
                    content,
                    copyContentBtn,
                    "Copy Content"
                );

            }
        );

    }


    /* =========================================================
       GENERIC COPY FUNCTION
       ========================================================= */

    async function copyText(
        text,
        button,
        originalText
    ) {

        try {

            if (
                navigator.clipboard &&
                window.isSecureContext
            ) {

                await navigator.clipboard.writeText(
                    text
                );

            } else {

                /*
                 * Fallback for HTTP/local development.
                 */

                const textarea =
                    document.createElement("textarea");

                textarea.value =
                    text;

                textarea.style.position =
                    "fixed";

                textarea.style.opacity =
                    "0";

                document.body.appendChild(
                    textarea
                );

                textarea.focus();

                textarea.select();

                document.execCommand("copy");

                textarea.remove();

            }


            if (button) {

                const oldText =
                    button.textContent;


                button.textContent =
                    "Copied!";


                setTimeout(
                    function () {

                        button.textContent =
                            oldText ||
                            originalText;

                    },
                    1500
                );

            }

        } catch (error) {

            console.error(
                "COPY ERROR:",
                error
            );


            alert(
                "Unable to copy."
            );

        }

    }


    /* =========================================================
       CLOSE ROOM
       ========================================================= */

    if (leaveRoomBtn) {

        leaveRoomBtn.addEventListener(
            "click",
            function () {

                stopRoomPolling();


                if (saveTimer) {

                    clearTimeout(saveTimer);

                    saveTimer = null;

                }


                currentRoomCode = null;

                isSaving = false;


                if (roomContent) {

                    roomContent.value = "";

                }


                if (roomCode) {

                    roomCode.textContent =
                        "------";

                }


                if (sharedContentSection) {

                    sharedContentSection.style.display =
                        "none";

                }


                if (generatedCodeSection) {

                    generatedCodeSection.style.display =
                        "none";

                }


                if (generatedRoomCode) {

                    generatedRoomCode.textContent =
                        "------";

                }


                if (pasteContent) {

                    pasteContent.value = "";

                }


                if (pasteCharacterCount) {

                    pasteCharacterCount.textContent =
                        "0 characters";

                }


                if (joinCode) {

                    joinCode.value = "";

                }


                updateCharacterCount();

                updatePasteCharacterCount();


                if (saveStatus) {

                    saveStatus.textContent =
                        "Ready";

                }


                if (roomStatus) {

                    roomStatus.textContent =
                        "Connected";

                }


                if (generateStatus) {

                    generateStatus.textContent =
                        "Ready";

                }

            }
        );

    }


    /* =========================================================
       PAGE CLEANUP
       ========================================================= */

    window.addEventListener(
        "beforeunload",
        function () {

            stopRoomPolling();


            if (saveTimer) {

                clearTimeout(saveTimer);

                saveTimer = null;

            }

        }
    );


    /* =========================================================
       INITIAL UI
       ========================================================= */

    updatePreview();

    updatePasteCharacterCount();

    updateCharacterCount();


});