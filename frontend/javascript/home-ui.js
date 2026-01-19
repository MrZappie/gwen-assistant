// home-ui.js

import { fetchFolder, fetchFile, saveFile } from "./home-file.js";

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

// --- CHAT SYSTEM LOGIC ---

const chatInput = document.getElementById("chat-input");
const chatSendBtn = document.getElementById("chat-send-btn");
const chatMessages = document.getElementById("chat-messages");
const historyList = document.getElementById("history-list");

// Tab Buttons
const tabChatBtn = document.getElementById("tab-chat-btn");
const tabHistoryBtn = document.getElementById("tab-history-btn");
const viewChat = document.getElementById("view-chat");
const viewHistory = document.getElementById("view-history");

// State
let currentSessionId = null; // If null, we create a new one on send
const STORAGE_KEY = "gwen_chat_sessions"; // LocalStorage key

// --- 1. Tab Switching ---
function switchTab(tabName) {
    if (tabName === 'chat') {
        tabChatBtn.classList.add('active');
        tabHistoryBtn.classList.remove('active');
        viewChat.classList.add('active');
        viewHistory.classList.remove('active');
        scrollToBottom();
    } else {
        tabHistoryBtn.classList.add('active');
        tabChatBtn.classList.remove('active');
        viewHistory.classList.add('active');
        viewChat.classList.remove('active');
        renderHistoryView(); // Refresh list when opening tab
    }
}

tabChatBtn.addEventListener("click", () => switchTab('chat'));
tabHistoryBtn.addEventListener("click", () => switchTab('history'));

// --- 2. Message Rendering ---
function renderMessage(content, type) {
    // remove placeholder if exists
    const placeholder = document.querySelector(".empty-chat-placeholder");
    if (placeholder) placeholder.remove();

    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${type}`;
    msgDiv.textContent = content;
    chatMessages.appendChild(msgDiv);
    scrollToBottom();
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// --- 3. History Management (Local Storage) ---

function getLocalSessions() {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
}

function saveSessionToLocal(id, firstMessage) {
    let sessions = getLocalSessions();
    const now = new Date();

    // Check if exists
    const existingIndex = sessions.findIndex(s => s.id === id);

    if (existingIndex > -1) {
        // Update existing
        sessions[existingIndex].lastMessage = firstMessage;
        sessions[existingIndex].timestamp = now.getTime();
        // Move to top
        const item = sessions.splice(existingIndex, 1)[0];
        sessions.unshift(item);
    } else {
        // Create new
        const newSession = {
            id: id,
            preview: firstMessage.substring(0, 30) + (firstMessage.length > 30 ? "..." : ""),
            lastMessage: firstMessage,
            timestamp: now.getTime()
        };
        sessions.unshift(newSession);
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
}

function renderHistoryView() {
    historyList.innerHTML = "";
    const sessions = getLocalSessions();

    if (sessions.length === 0) {
        historyList.innerHTML = `<div style="text-align:center; color:#666; padding:20px;">No history found.</div>`;
        return;
    }

    sessions.forEach(session => {
        const dateStr = new Date(session.timestamp).toLocaleDateString();

        const card = document.createElement("div");
        card.className = `history-card ${currentSessionId === session.id ? 'active-session' : ''}`;

        card.innerHTML = `
         <div class="h-card-header">
        <span>Chat</span>
        <div class="h-card-actions">
            <span class="h-card-date">${dateStr}</span>
            <i class="bi bi-trash delete-chat-btn"></i>
        </div>
    </div>
    <div class="h-card-preview">${session.lastMessage}</div>
`;
        const deleteBtn = card.querySelector(".delete-chat-btn");

        deleteBtn.addEventListener("click", (e) => {
            e.stopPropagation(); // prevent opening chat
            deleteSession(session.id);
        });

        card.addEventListener("click", () => loadSession(session.id));
        historyList.appendChild(card);
    });
}

// --- 4. API & Interaction ---

async function loadSession(sessionId) {
    currentSessionId = sessionId;
    switchTab('chat');
    chatMessages.innerHTML = ""; // Clear current view

    // Fetch from Backend
    try {
        const res = await fetch(`/api/chat/${sessionId}`); // Note: You need to ensure your FastAPI router prefix is handled
        // If your router is just /chat/{id}, remove /api or configure main.py

        const messages = await res.json();

        if (Array.isArray(messages)) {
            messages.forEach(msg => {
                // Adapt based on how your backend stores 'type' or 'role'
                // Based on your python: human/ai
                const type = (msg.type === "human" || msg.type === "user") ? "user" : "system";
                renderMessage(msg.content, type);
            });
        }
    } catch (err) {
        console.error("Failed to load chat", err);
        renderMessage("Error loading history.", "system");
    }
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = "";

    // 1. DEFAULT BEHAVIOR: If no session is loaded, make a new one
    if (!currentSessionId) {
        currentSessionId = crypto.randomUUID();
        console.log("Starting new session:", currentSessionId);
    }

    // 2. Render User Message immediately
    renderMessage(text, "user");

    // 3. Send to Backend
    try {
        const response = await fetch(`/api/chat/${currentSessionId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) throw new Error("Failed to reach backend");

        // 4. Update Local History (Sidebar preview)
        // We do this after the fetch starts so it only appears if the message "went through"
        saveSessionToLocal(currentSessionId, text);

        // 5. Handle Streaming Response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split("\n");

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const data = JSON.parse(line);
                    if (data.type === "ai" || data.type === "AIMessage") {
                        renderMessage(data.content, "system");
                        // Optional: Update preview to show the AI's last words
                        saveSessionToLocal(currentSessionId, "AI: " + data.content);
                    }
                } catch (e) {
                    // Ignore partial JSON chunks during streaming
                }
            }
        }
    } catch (err) {
        console.error("Chat Error:", err);
        renderMessage("Connection error. Message not saved.", "system");
    }
}

// Event Listeners
chatSendBtn.addEventListener("click", sendMessage);
chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function deleteSession(sessionId) {
    if (!confirm("Delete this chat permanently?")) return;

    try {
        const res = await fetch(`/api/chat/${sessionId}`, {
            method: "DELETE"
        });

        if (!res.ok) throw new Error("Delete failed");

        // Remove from localStorage
        let sessions = getLocalSessions().filter(s => s.id !== sessionId);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));

        // Reset UI if deleting active chat
        if (currentSessionId === sessionId) {
            currentSessionId = null;
            chatMessages.innerHTML = "";
            renderMessage("Chat deleted.", "system");
        }

        renderHistoryView();

    } catch (err) {
        console.error("Delete error:", err);
        alert("Failed to delete chat.");
    }
}
