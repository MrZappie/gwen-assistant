// home-ui.js

import { fetchFolder, fetchFile } from "./home-file.js";

const folderCache = new Map();
const treeContainer = document.getElementById("folder-tree");

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
        div.onclick = async () => {
            const file = await fetchFile(item.path);
            console.log(file.content);
        };
    }

    return li;
}


// Dropdown Menu Logic
function toggleDropdown(id) {
    // 1. Get the specific dropdown we want to toggle
    const target = document.getElementById(id);
    const isCurrentlyShow = target.classList.contains("show");

    // 2. Close ALL dropdowns first
    const dropdowns = document.getElementsByClassName("dropdown-content");
    for (let i = 0; i < dropdowns.length; i++) {
        dropdowns[i].classList.remove('show');
    }

    // 3. If the one we clicked wasn't already open, open it
    if (!isCurrentlyShow) {
        target.classList.add("show");
    }
}

// Ensure the window click doesn't close the menu immediately when clicking the button
window.onclick = function(event) {
    if (!event.target.matches('.nav-btn')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            if (dropdowns[i].classList.contains('show')) {
                dropdowns[i].classList.remove('show');
            }
        }
    }
};
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("/api/project-status");
        const data = await res.json();

        if (!data.project_directory) {
            window.location.replace("index.html");
        }else {
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

// home-ui.js (after DOMContentLoaded or at the bottom)
const closeFolderBtn = document.getElementById("close-folder-btn");

closeFolderBtn.addEventListener("click", async () => {
    try {
        const res = await fetch("/api/close-project");
        const data = await res.json();

        if (!data.error) {
            // Clear the tree
            treeContainer.innerHTML = "";
            folderCache.clear();

            window.location.reload();

            // Optionally, show a message
            console.log("Project closed successfully");
        }
    } catch (err) {
        console.error("Failed to close project", err);
    }

    // Hide dropdown
    document.getElementById("project-menu").classList.remove("show");
});


window.toggleDropdown = toggleDropdown;