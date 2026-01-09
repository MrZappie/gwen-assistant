// home-ui.js

import { fetchFolder, fetchFile } from "./home-file.js";

const folderCache = new Map();
const treeContainer = document.getElementById("folder-tree");

// References to the editor elements in the center area
const fileEditor = document.getElementById("file-editor");
const tabsContainer = document.getElementById("tabs-container");

// State to track open files and active path
const openFiles = new Map();
let activeFilePath = null;

function createTreeItem(item) {
    const li = document.createElement("li");
    const div = document.createElement("div");
    div.className = "tree-item";

    const icon = document.createElement("i");
    icon.classList.add("bi");
    const label = document.createElement("span");
    label.textContent = item.name;

    if (item.type === "folder") {
        icon.classList.add("bi-folder");
    } else {
        icon.classList.add("bi-file-earmark");
    }

    div.appendChild(icon);
    div.appendChild(label);
    li.appendChild(div);

    if (item.type === "folder") {
        const ul = document.createElement("ul");
        ul.className = "nested";
        li.appendChild(ul);

        div.onclick = async () => {
            ul.classList.toggle("active");
            icon.classList.toggle("bi-folder");
            icon.classList.toggle("bi-folder2-open");

            if (folderCache.has(item.path)) return;

            const children = await fetchFolder(item.path);
            folderCache.set(item.path, children);

            children.forEach(child => {
                ul.appendChild(createTreeItem(child));
            });
        };
    } else {
        // UPDATED: Now uses the tab-management logic
        div.onclick = () => openFile(item);
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
    // Save current editor content back to the Map before switching
    if (activeFilePath && openFiles.has(activeFilePath)) {
        openFiles.get(activeFilePath).content = fileEditor.value;
    }

    activeFilePath = path;
    const fileData = openFiles.get(path);
    fileEditor.value = fileData.content;
    
    // Highlight the file in the sidebar tree
    document.querySelectorAll('.tree-item').forEach(el => el.classList.remove('selected-file'));
    // (Logic to find and highlight sidebar item could be added here)
    
    renderTabs();
}

function closeFile(path) {
    openFiles.delete(path);
    if (activeFilePath === path) {
        activeFilePath = Array.from(openFiles.keys())[0] || null;
        fileEditor.value = activeFilePath ? openFiles.get(activeFilePath).content : "";
    }
    renderTabs();
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

        if (!data.project_directory) {
            window.location.replace("index.html");
        } else {
            const rootPath = data.project_directory;
            const rootChildren = await fetchFolder(rootPath);
            folderCache.set(rootPath, rootChildren);

            const ul = document.createElement("ul");
            rootChildren.forEach(item => ul.appendChild(createTreeItem(item)));
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