// 1. Define your project structure
const projectData = [
    {
        name: "Simple Calculator",
        type: "folder",
        children: [
            { name: "ReadMe.md", type: "file" },
            { name: "main.py", type: "file" },

        ]
    }
];

const folderInput = document.getElementById('folder-input');
const openFolderBtn = document.getElementById('open-folder-btn');
const treeContainer = document.getElementById('folder-tree');

// 1. Trigger the hidden input when the dropdown item is clicked
openFolderBtn.addEventListener('click', () => {
    folderInput.click();
});

// 2. Handle the selected files
folderInput.addEventListener('change', (event) => {
    const files = event.target.files;
    if (files.length > 0) {
        // Clear the existing tree
        treeContainer.innerHTML = '';

        // Convert the flat file list into a nested structure
        const structuredData = buildHierarchy(files);

        // Render the new tree
        createTree(structuredData, treeContainer);
    }
});

// 3. Helper function to turn flat paths into a Tree Object
function buildHierarchy(fileList) {
    const root = [];

    Array.from(fileList).forEach(file => {
        const pathParts = file.webkitRelativePath.split('/');
        let currentLevel = root;

        pathParts.forEach((part, index) => {
            const isFile = index === pathParts.length - 1;
            let existingPath = currentLevel.find(item => item.name === part);

            if (!existingPath) {
                existingPath = {
                    name: part,
                    type: isFile ? 'file' : 'folder',
                    children: isFile ? null : []
                };
                currentLevel.push(existingPath);
            }

            if (!isFile) {
                currentLevel = existingPath.children;
            }
        });
    });
    return root;
}
// 2. Function to create the HTML for the tree
function createTree(data, container) {
    const ul = document.createElement('ul');
    ul.className = 'tree-list';

    data.forEach(item => {
        const li = document.createElement('li');
        const itemDiv = document.createElement('div');
        itemDiv.className = 'tree-item';

        // --- MODIFIED SECTION ---
        // Instead of plain emojis, use a span for the icon
        const iconSpan = document.createElement('span');
        iconSpan.className = 'tree-icon';

        // If it's a file, you might want a different icon or none
        if (item.type != 'file') {
            itemDiv.appendChild(iconSpan);
        }

        const textSpan = document.createElement('span');
        textSpan.textContent = item.name;

        itemDiv.appendChild(textSpan);
        // -------------------------

        li.appendChild(itemDiv);

        if (item.type === 'folder' && item.children) {
            const nestedUl = document.createElement('div');
            nestedUl.className = 'nested active';

            // Set initial state for the icon if it starts active
            itemDiv.classList.add('open');

            createTree(item.children, nestedUl);
            li.appendChild(nestedUl);

            itemDiv.addEventListener('click', () => {
                nestedUl.classList.toggle('active');
                // This toggle triggers the CSS transform: rotate
                itemDiv.classList.toggle('open');
            });
        }

        ul.appendChild(li);
    });

    container.appendChild(ul);
}
// 3. Initialize the tree on page load
document.addEventListener('DOMContentLoaded', () => {
    const treeContainer = document.getElementById('folder-tree');
    createTree(projectData, treeContainer);
});

// 4. Dropdown Menu Logic
function toggleDropdown(id) {
    // Close all other dropdowns first
    const dropdowns = document.getElementsByClassName("dropdown-content");
    for (let i = 0; i < dropdowns.length; i++) {
        if (dropdowns[i].id !== id) {
            dropdowns[i].classList.remove('show');
        }
    }
    // Toggle the clicked one
    document.getElementById(id).classList.toggle("show");
}

// Close dropdowns if user clicks outside
window.onclick = function (event) {
    if (!event.target.matches('.nav-btn')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            dropdowns[i].classList.remove('show');
        }
    }
}