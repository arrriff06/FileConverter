// =====================================================
// ROOM SYSTEM
// =====================================================

const createRoomBtn = document.getElementById("createRoomBtn");
const joinRoomBtn = document.getElementById("joinRoomBtn");

const joinCode = document.getElementById("joinCode");

const roomStart = document.getElementById("roomStart");
const roomEditor = document.getElementById("roomEditor");

const roomCode = document.getElementById("roomCode");
const roomContent = document.getElementById("roomContent");

const copyRoomCodeBtn =
    document.getElementById("copyRoomCodeBtn");

const copyContentBtn =
    document.getElementById("copyContentBtn");

const leaveRoomBtn =
    document.getElementById("leaveRoomBtn");

const characterCount =
    document.getElementById("characterCount");

const saveStatus =
    document.getElementById("saveStatus");

const roomStatus =
    document.getElementById("roomStatus");

const typeButtons =
    document.querySelectorAll(".type-btn");


let currentRoom = null;
let currentType = "text";

let updateTimer = null;
let refreshTimer = null;


// =====================================================
// CREATE ROOM
// =====================================================

createRoomBtn.addEventListener("click", async () => {

    createRoomBtn.disabled = true;
    createRoomBtn.innerText = "Creating...";

    try {

        const response = await fetch("/room/create", {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || "Unable to create room."
            );
        }

        openRoom(data.code, "", "text");

    } catch (error) {

        alert(error.message);

    } finally {

        createRoomBtn.disabled = false;
        createRoomBtn.innerText = "Create Room";
    }

});


// =====================================================
// JOIN ROOM
// =====================================================

joinRoomBtn.addEventListener("click", joinRoom);

joinCode.addEventListener("keydown", (event) => {

    if (event.key === "Enter") {
        joinRoom();
    }

});


async function joinRoom() {

    const code = joinCode.value
        .trim()
        .toUpperCase();

    if (!code) {
        alert("Enter a room code.");
        return;
    }

    if (code.length !== 6) {
        alert("Room code must contain 6 characters.");
        return;
    }

    joinRoomBtn.disabled = true;
    joinRoomBtn.innerText = "Joining...";

    try {

        const response = await fetch(
            `/room/${encodeURIComponent(code)}`
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || "Room not found."
            );
        }

        openRoom(
            data.code,
            data.content,
            data.type
        );

    } catch (error) {

        alert(error.message);

    } finally {

        joinRoomBtn.disabled = false;
        joinRoomBtn.innerText = "Join Room";
    }
}


// =====================================================
// OPEN ROOM
// =====================================================

function openRoom(code, content, type) {

    currentRoom = code;

    currentType = type || "text";

    roomCode.innerText = code;

    roomContent.value = content || "";

    roomStart.style.display = "none";

    roomEditor.style.display = "block";

    updateCharacterCount();

    setActiveType(currentType);

    startRoomRefresh();

    window.scrollTo({
        top: roomEditor.offsetTop - 30,
        behavior: "smooth"
    });
}


// =====================================================
// CHARACTER COUNT
// =====================================================

function updateCharacterCount() {

    const count = roomContent.value.length;

    characterCount.innerText =
        `${count.toLocaleString()} characters`;
}

roomContent.addEventListener(
    "input",
    updateCharacterCount
);


// =====================================================
// SAVE / UPDATE ROOM
// =====================================================

roomContent.addEventListener("input", () => {

    if (!currentRoom) return;

    saveStatus.innerText = "Saving...";

    clearTimeout(updateTimer);

    updateTimer = setTimeout(
        updateRoom,
        500
    );

});


async function updateRoom() {

    if (!currentRoom) return;

    try {

        const response = await fetch(
            `/room/${currentRoom}/update`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    content: roomContent.value,
                    type: currentType
                })
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || "Save failed."
            );
        }

        saveStatus.innerText = "Saved";

    } catch (error) {

        saveStatus.innerText = "Save failed";

        console.error(error);
    }
}


// =====================================================
// ROOM REFRESH
// =====================================================

function startRoomRefresh() {

    stopRoomRefresh();

    refreshTimer = setInterval(
        refreshRoom,
        2000
    );
}


function stopRoomRefresh() {

    if (refreshTimer) {

        clearInterval(refreshTimer);

        refreshTimer = null;
    }
}


async function refreshRoom() {

    if (!currentRoom) return;

    try {

        const response = await fetch(
            `/room/${currentRoom}`
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            roomStatus.innerText = "Room unavailable";

            return;
        }

        roomStatus.innerText = "Connected";

        /*
         * Don't overwrite the user's text while
         * they're actively typing.
         */
        if (
            document.activeElement !== roomContent
        ) {

            if (
                data.content !== roomContent.value
            ) {

                roomContent.value =
                    data.content || "";

                updateCharacterCount();
            }
        }

    } catch (error) {

        roomStatus.innerText = "Connection lost";

        console.error(error);
    }
}


// =====================================================
// COPY ROOM CODE
// =====================================================

copyRoomCodeBtn.addEventListener(
    "click",
    async () => {

        if (!currentRoom) return;

        try {

            await navigator.clipboard.writeText(
                currentRoom
            );

            copyRoomCodeBtn.innerText = "Copied!";

            setTimeout(() => {

                copyRoomCodeBtn.innerText = "Copy";

            }, 1500);

        } catch (error) {

            alert("Unable to copy room code.");
        }

    }
);


// =====================================================
// COPY CONTENT
// =====================================================

copyContentBtn.addEventListener(
    "click",
    async () => {

        const content = roomContent.value;

        if (!content) {

            alert("There is nothing to copy.");

            return;
        }

        try {

            await navigator.clipboard.writeText(
                content
            );

            copyContentBtn.innerText =
                "Copied!";

            setTimeout(() => {

                copyContentBtn.innerText =
                    "Copy Content";

            }, 1500);

        } catch (error) {

            alert("Unable to copy content.");
        }

    }
);


// =====================================================
// TEXT / CODE MODE
// =====================================================

typeButtons.forEach(button => {

    button.addEventListener("click", async () => {

        currentType =
            button.dataset.type;

        setActiveType(currentType);

        if (currentRoom) {
            await updateRoom();
        }

    });

});


function setActiveType(type) {

    typeButtons.forEach(button => {

        button.classList.toggle(
            "active",
            button.dataset.type === type
        );

    });
}


// =====================================================
// LEAVE ROOM
// =====================================================

leaveRoomBtn.addEventListener(
    "click",
    async () => {

        if (!currentRoom) return;

        const shouldLeave = confirm(
            "Leave this room?"
        );

        if (!shouldLeave) return;

        stopRoomRefresh();

        currentRoom = null;

        roomEditor.style.display = "none";

        roomStart.style.display = "grid";

        roomContent.value = "";

        joinCode.value = "";

        updateCharacterCount();

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    }
);