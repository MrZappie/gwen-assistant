// home-ui.js

import { fetchFolder, fetchFile , saveFile } from "./home-file.js";

const folderCache = new Map();
const treeContainer = document.getElementById("folder-tree");

// References to the editor elements in the center area
const fileEditor = document.getElementById("file-editor");
const tabsContainer = document.getElementById("tabs-container");
const emptyState = document.getElementById("empty-state");

// State to track open files and active path
const openFiles = new Map();
let activeFilePath = null;

function sortItems(items) {
    if (!Array.isArray(items)) return [];

    return [...items].sort((a, b) => {
        if (a.type !== b.type) {
            return a.type === "folder" ? -1 : 1;
        }
        return a.name.toLowerCase().localeCompare(b.name.toLowerCase());
    });
}


function createTreeItem(item) {
    const li = document.createElement("li");
    const row = document.createElement("div");
    row.className = "tree-item";

    const icon = document.createElement("i");
    icon.className = item.type === "folder"
        ? "bi bi-folder"
        : "bi bi-file-earmark";

    const label = document.createElement("span");
    label.textContent = item.name;

    row.appendChild(icon);
    row.appendChild(label);
    li.appendChild(row);

    if (item.type === "folder") {
        const childrenContainer = document.createElement("ul");
        childrenContainer.className = "nested";
        li.appendChild(childrenContainer);

        let loaded = false;

        row.addEventListener("click", async () => {
            childrenContainer.classList.toggle("active");

            icon.className = childrenContainer.classList.contains("active")
                ? "bi bi-folder2-open"
                : "bi bi-folder";

            if (loaded) return;
            loaded = true;

            try {
                console.log("Loading folder:", item.path);   // DEBUG

                const raw = await fetchFolder(item.path);
                console.table(raw);                          // DEBUG

                const children = sortItems(raw);

                children.forEach(child => {
                    childrenContainer.appendChild(createTreeItem(child));
                });
            } catch (err) {
                console.error("Folder load failed:", err);
            }
        });
    } else {
        row.addEventListener("click", () => openFile(item));
    }

    return li;
}


function renderTabs() {
    tabsContainer.innerHTML = "";
    openFiles.forEach((fileData, path) => {
        const tab = document.createElement("div");
        tab.className = `tab ${path === activeFilePath ? "active" : ""}`;

        const label = document.createElement("span");
        label.textContent = fileData.name;
        label.onclick = () => switchToFile(path);

        const closeBtn = document.createElement("i");
        closeBtn.className = "bi bi-x";
        closeBtn.onclick = (e) => {
            e.stopPropagation();
            closeFile(path);
        };

        tab.appendChild(label);
        tab.appendChild(closeBtn);
        tabsContainer.appendChild(tab);
    });
}

async function openFile(item) {
    if (!openFiles.has(item.path)) {
        try {
            const file = await fetchFile(item.path); //
            openFiles.set(item.path, { name: item.name, content: file.content });
        } catch (err) {
            console.error("Error opening file", err);
            return;
        }
    }
    switchToFile(item.path);
}

function switchToFile(path) {
    // 1. Save content of the PREVIOUS active file before switching
    if (activeFilePath && openFiles.has(activeFilePath)) {
        openFiles.get(activeFilePath).content = fileEditor.value;
    }

    activeFilePath = path;

    // 2. TOGGLE VIEW: Show Editor OR Show "Select a File"
    if (path) {
        // CASE A: We have a valid file path
        const fileData = openFiles.get(path);
        fileEditor.value = fileData ? fileData.content : "";

        fileEditor.style.display = "block";       // Show Editor
        if (emptyState) emptyState.style.display = "none"; // Hide Empty Screen
    } else {
        // CASE B: Path is null (No file selected)
        fileEditor.style.display = "none";        // Hide Editor
        if (emptyState) emptyState.style.display = "flex"; // Show Empty Screen
    }

    renderTabs();
}

function closeFile(path) {
    // 1. Remove file from memory
    openFiles.delete(path);

    // 2. CHECK: If NO files are left, show the empty screen
    if (openFiles.size === 0) {
        switchToFile(null); // This triggers the empty state
    }
    // 3. If we closed the active file, switch to another one
    else if (activeFilePath === path) {
        const remainingFiles = Array.from(openFiles.keys());
        const lastFile = remainingFiles[remainingFiles.length - 1];
        switchToFile(lastFile);
    }
    else {
        renderTabs();
    }
}

// Dropdown Menu Logic
function toggleDropdown(id) {
    const target = document.getElementById(id);
    const dropdowns = document.getElementsByClassName("dropdown-content");
    for (let i = 0; i < dropdowns.length; i++) {
        if (dropdowns[i].id !== id) dropdowns[i].classList.remove('show');
    }
    target.classList.toggle("show");
}

window.onclick = function (event) {
    if (!event.target.matches('.nav-btn')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            dropdowns[i].classList.remove('show');
        }
    }
};

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/api/project-status"); //
        const data = await res.json();
        switchToFile(null);
        if (!data.project_directory) {
            window.location.replace("index.html");
        } else {
            const rootPath = "";   // root must always be empty string

            const rootItem = {
                name: data.project_directory.split(/[\\/]/).pop(), // show folder name only
                path: rootPath,
                type: "folder"
            };

            const ul = document.createElement("ul");
            ul.appendChild(createTreeItem(rootItem));
            treeContainer.appendChild(ul);


        }
    } catch (err) {
        console.error("Backend not reachable", err);
    }
});

const closeFolderBtn = document.getElementById("close-folder-btn");
closeFolderBtn.addEventListener("click", async () => {
    try {
        const res = await fetch("/api/close-project"); //
        const data = await res.json();
        if (!data.error) {
            treeContainer.innerHTML = "";
            folderCache.clear();
            window.location.reload();
        }
    } catch (err) {
        console.error("Failed to close project", err);
    }
});

const sidebar = document.getElementById("sidebar");
const resizer = document.getElementById("resizer");

resizer.addEventListener("mousedown", (e) => {
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
    const doDrag = (e) => {
        const newWidth = e.clientX - sidebar.getBoundingClientRect().left;
        if (newWidth > 150 && newWidth < 600) sidebar.style.width = `${newWidth}px`;
    };
    const stopDrag = () => {
        document.body.style.cursor = "default";
        document.body.style.userSelect = "auto";
        window.removeEventListener("mousemove", doDrag);
        window.removeEventListener("mouseup", stopDrag);
    };
    window.addEventListener("mousemove", doDrag);
    window.addEventListener("mouseup", stopDrag);
});

window.toggleDropdown = toggleDropdown;

// --- Right Panel Resizer Logic ---
const rightResizer = document.getElementById("right-resizer");
const rightPanel = document.getElementById("right-panel");

if (rightResizer && rightPanel) {
    rightResizer.addEventListener("mousedown", (e) => {
        e.preventDefault();
        document.body.style.cursor = "col-resize";
        document.body.style.userSelect = "none"; // Stop text highlighting

        const doDragRight = (e) => {
            // Calculate width: Window Total Width - Mouse Position = Panel Width
            const newWidth = window.innerWidth - e.clientX;

            // Optional: Limit width between 150px and 600px
            if (newWidth > 150 && newWidth < 600) {
                rightPanel.style.width = `${newWidth}px`;
            }
        };

        const stopDragRight = () => {
            document.body.style.cursor = "default";
            document.body.style.userSelect = "auto";
            window.removeEventListener("mousemove", doDragRight);
            window.removeEventListener("mouseup", stopDragRight);
        };

        window.addEventListener("mousemove", doDragRight);
        window.addEventListener("mouseup", stopDragRight);
    });
} else {
    console.error("Right panel or resizer not found. Check HTML IDs.");
}

async function handleSave() {
    if (!activeFilePath) return;

    const content = fileEditor.value;
    
    try {
        // Show some loading state if you want
        console.log("Saving...", activeFilePath);
        
        await saveFile(activeFilePath, content);
        
        // Update local cache so switching tabs doesn't overwrite with old data
        if (openFiles.has(activeFilePath)) {
            openFiles.get(activeFilePath).content = content;
        }
        
        alert("File saved successfully!"); 
    } catch (err) {
        console.error("Save failed:", err);
        alert("Error saving file.");
    }
}

// 4. Add Keyboard Shortcut (Ctrl + S)
document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault(); // Stop browser from trying to save the HTML page
        handleSave();
    }
});

// --- Chat Logic ---

// --- Advanced Chat Logic with History ---

const chatInput = document.getElementById("chat-input");
const chatSendBtn = document.getElementById("chat-send-btn");
const chatMessages = document.getElementById("chat-messages");
const newChatBtn = document.getElementById("new-chat-btn");
const historyDropdown = document.getElementById("chat-history-dropdown");

// State
let savedChats = [];     // Stores old chats: [{ title: "Hi...", messages: [...] }]
let currentSession = []; // Stores currently visible messages

// 1. Function to Render a Single Message to DOM
function renderMessage(text, type) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${type}`;
    msgDiv.textContent = text;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 2. Send Message Logic
function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Save to memory
    currentSession.push({ text: text, type: "user" });
    
    // Render to screen
    renderMessage(text, "user");
    
    chatInput.value = "";

    // Simulate System Reply (Optional)
    setTimeout(() => {
        const reply = "Echo: " + text;
        currentSession.push({ text: reply, type: "system" });
        renderMessage(reply, "system");
    }, 500);
}

// 3. NEW CHAT Logic
newChatBtn.addEventListener("click", () => {
    // Only save if the current session actually has messages
    if (currentSession.length > 0) {
        
        // Generate a title (first 15 chars of first message)
        const firstMsg = currentSession[0].text;
        const title = firstMsg.length > 15 ? firstMsg.substring(0, 15) + "..." : firstMsg;
        
        // Save to History Array
        savedChats.push({
            id: Date.now(),
            title: title,
            messages: [...currentSession] // Clone array
        });

        // Add to Dropdown
        const option = document.createElement("option");
        option.value = savedChats.length - 1; // Index in savedChats array
        option.textContent = title;
        historyDropdown.appendChild(option);
    }

    // Reset UI for fresh start
    currentSession = [];
    chatMessages.innerHTML = "";
    historyDropdown.value = "current"; // Reset dropdown to 'Current'
});

// 4. LOAD OLD CHAT Logic (Dropdown Change)
historyDropdown.addEventListener("change", (e) => {
    const value = e.target.value;

    // Clear current view
    chatMessages.innerHTML = "";

    if (value === "current") {
        // If user switches back to "Current Session" (if we want to support that logic)
        // For now, "New Chat" clears current, so 'current' is just empty.
        currentSession.forEach(msg => renderMessage(msg.text, msg.type));
    } else {
        // Load data from savedChats
        const chatIndex = parseInt(value);
        const oldChat = savedChats[chatIndex];
        
        // Render old messages
        oldChat.messages.forEach(msg => renderMessage(msg.text, msg.type));
        
        // IMPORTANT: We are viewing history. 
        // Any new messages typed here will technically be part of this 'current view'
        // unless you want to lock old chats. 
        // For simplicity, we copy it back to currentSession to allow continuing the chat.
        currentSession = [...oldChat.messages];
    }
});

// Event Listeners for Sending
chatSendBtn.addEventListener("click", sendMessage);
chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});