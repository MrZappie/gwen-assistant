// 1. Display Logic
const projectData = [
    {
        name: ".venv",
        type: "folder",
        children: []
    },
    {
        name: "backend",
        type: "folder",
        children: []
    },
    {
        name: "frontend",
        type: "folder",
        isOpen: true,
        children: [
            {
                name: "javascript",
                type: "folder",
                children: [
                    { name: "home-ui.js", type: "file", ext: "js" },
                    { name: "index.js", type: "file", ext: "js" }
                ]
            },
            {
                name: "stylesheet",
                type: "folder",
                children: [
                    { name: "home.css", type: "file", ext: "css" },
                    { name: "index.css", type: "file", ext: "css" }
                ]
            },
            { name: "home.html", type: "file", ext: "html" },
            { name: "index.html", type: "file", ext: "html" }
        ]
    },
    { name: ".gitignore", type: "file", ext: "git" },
    { name: "LICENSE", type: "file", ext: "license" },
    { name: "requirements.txt", type: "file", ext: "txt" }
];

function createTree(data, container) {
    const ul = document.createElement('ul');
    ul.className = 'tree-list';

    data.forEach(item => {
        const li = document.createElement('li');
        const itemContent = document.createElement('div');
        itemContent.className = `tree-item ${item.type}`;

        // Add Chevron for folders
        if (item.type === 'folder') {
            const icon = document.createElement('span');
            icon.className = 'chevron';
            icon.innerHTML = '›'; // Right arrow
            itemContent.appendChild(icon);
        }

        const nameLabel = document.createElement('span');
        nameLabel.textContent = item.name;
        itemContent.appendChild(nameLabel);
        li.appendChild(itemContent);

        if (item.type === 'folder' && item.children) {
            const childContainer = document.createElement('div');
            childContainer.className = 'nested';

            // Toggle logic
            itemContent.onclick = (e) => {
                e.stopPropagation();
                itemContent.classList.toggle('open');
                childContainer.classList.toggle('active');
            };

            createTree(item.children, childContainer);
            li.appendChild(childContainer);
        }

        ul.appendChild(li);
    });

    container.appendChild(ul);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const treeRoot = document.getElementById('folder-tree');
    createTree(projectData, treeRoot);
});

function toggleDropdown(menuId) {
    // Close all other dropdowns first
    const dropdowns = document.getElementsByClassName("dropdown-content");
    for (let i = 0; i < dropdowns.length; i++) {
        if (dropdowns[i].id !== menuId) {
            dropdowns[i].classList.remove('show');
        }
    }
    
    // Toggle the clicked dropdown
    document.getElementById(menuId).classList.toggle("show");
}

// Close the dropdown if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.nav-btn')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            const openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}