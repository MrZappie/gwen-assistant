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

let currentSessionId = null;

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
function markdownToHtml(text) {
    if (!text) return "";
    let html = escapeHtml(text);

    // Code blocks
    html = html.replace(/```([\s\S]+?)```/g, (_, code) =>
        `<pre>${code.trim()}</pre>`
    );

    // Tables
    const lines = html.split("\n");
    let inTable = false;
    for (let i = 0; i < lines.length; i++) {
        if (/^\|(.+)\|$/.test(lines[i])) {
            if (!inTable) {
                lines[i] =
                    "<table><thead>" +
                    renderTableRow(lines[i], true) +
                    "</thead><tbody>";
                inTable = true;
                if (lines[i + 1] && lines[i + 1].includes("|---"))
                    lines[i + 1] = "";
            } else {
                lines[i] = renderTableRow(lines[i], false);
            }
        } else if (inTable) {
            lines[i - 1] += "</tbody></table>";
            inTable = false;
        }
    }
    html = lines.filter(l => l !== "").join("\n");

    // Headers
    html = html
        .replace(/^### (.*$)/gim, "<h3>$1</h3>")
        .replace(/^## (.*$)/gim, "<h2>$1</h2>")
        .replace(/^# (.*$)/gim, "<h1>$1</h1>");

    // Lists
    html = html.replace(/^\s*-\s+(.*)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>)/gs, "<ul>$1</ul>");
    html = html.replace(/<\/ul>\n<ul>/g, "");

    // Bold / Italic / Inline code
    html = html
        .replace(/\*\*([^\*]+)\*\*/g, "<b>$1</b>")
        .replace(/\*([^\*]+)\*/g, "<i>$1</i>")
        .replace(/`([^`]+)`/g, "<code>$1</code>");

    // Line breaks
    return html
        .split("\n")
        .map(line =>
            line.match(/<(table|thead|tbody|tr|td|th|ul|ol|li|pre|h\d)/)
                ? line
                : line + "<br>"
        )
        .join("");
}

function renderTableRow(row, isHeader) {
    const cells = row.split("|").filter(c => c.trim() !== "");
    const tag = isHeader ? "th" : "td";
    return `<tr>${cells
        .map(c => `<${tag}>${c.trim()}</${tag}>`)
        .join("")}</tr>`;
}

function escapeHtml(str) {
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}



function renderMessageFormatted(msg) {
    const placeholder = document.querySelector(".empty-chat-placeholder");
    if (placeholder) placeholder.remove();

    const role =
        msg.type === "human" || msg.type === "user" ? "user" : "ai";

    const content =
        msg.content || (msg.kwargs && msg.kwargs.content) || "";

    const div = document.createElement("div");
    div.className = `message ${role}`;

    const label = document.createElement("div");
    label.className = "role-label";
    label.innerText = role === "user" ? "You" : "Agent";
    div.appendChild(label);

    const contentDiv = document.createElement("div");
    contentDiv.innerHTML = markdownToHtml(content);
    div.appendChild(contentDiv);

    chatMessages.appendChild(div);
    scrollToBottom();
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// --- 3. History Management (Local Storage) ---


async function renderHistoryView() {
    historyList.innerHTML = `<div style="padding:10px;color:#666;">Loading…</div>`;

    try {
        const res = await fetch("/api/sessions");
        if (!res.ok) throw new Error("Failed to load sessions");

        const sessions = await res.json();
        historyList.innerHTML = "";

        if (!sessions.length) {
            historyList.innerHTML = `
              <div style="text-align:center; color:#666; padding:20px;">
                No history found.
              </div>`;
            return;
        }

        sessions.forEach(session => {
            const dateStr = new Date(session.timestamp).toLocaleDateString();

            const card = document.createElement("div");
            card.className = `history-card ${currentSessionId === session.id ? "active-session" : ""
                }`;

            card.innerHTML = `
              <div class="h-card-header">
                <span>Chat</span>
                <span class="h-card-date">${dateStr}</span>
              </div>
              <div class="h-card-preview">
                ${session.lastMessage || "New conversation"}
              </div>
            `;

            card.addEventListener("click", () => loadSession(session.id));
            historyList.appendChild(card);
        });

    } catch (err) {
        console.error(err);
        historyList.innerHTML = `
          <div style="color:red; padding:20px;">
            Failed to load history
          </div>`;
    }
}

// --- 4. API & Interaction ---

async function loadSession(sessionId) {
    currentSessionId = sessionId;
    switchTab("chat");
    chatMessages.innerHTML = "";

    try {
        const res = await fetch(`/api/chat/${sessionId}`);
        if (!res.ok) throw new Error("Failed to load chat");

        const messages = await res.json();

        messages.forEach(msg => {
            if (msg.type === "tool") return;

            renderMessageFormatted(msg);
        });

    } catch (err) {
        console.error(err);
        renderMessageFormatted({
            type: "ai",
            content: "Failed to load chat history."
        });
    }
}

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    chatInput.value = "";

    if (!currentSessionId) {
        currentSessionId = crypto.randomUUID();
        console.log("New session:", currentSessionId);
    }

    renderMessageFormatted({
        type: "human",
        content: text
    });

    try {
        const response = await fetch(`/api/chat/${currentSessionId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/x-ndjson"
            },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) throw new Error("Backend error");

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const event = JSON.parse(line);
                    if (event.type !== "tool") {
                        renderMessageFormatted(event);
                    }
                } catch (_) { }
            }
        }
        renderHistoryView();

    } catch (err) {
        console.error(err);
        renderMessageFormatted({
            type: "ai",
            content: "Connection error."
        });
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

function startNewChat() {
    currentSessionId = crypto.randomUUID();
    chatMessages.innerHTML = `
        <div class="empty-chat-placeholder">
            <i class="bi bi-chat-square-text"></i>
            <p>Start a new conversation...</p>
        </div>
    `;
    switchTab("chat");
}

window.startNewChat = startNewChat;
