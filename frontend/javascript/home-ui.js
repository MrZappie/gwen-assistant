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
        if (item.type === 'file') {
            iconSpan.style.visibility = 'hidden'; // Hide icon for files, or change code
        }

        const textSpan = document.createElement('span');
        textSpan.textContent = item.name;

        itemDiv.appendChild(iconSpan);
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