// 1. Define your project structure
const projectData = [
    {
        name: "Simple Calculator",
        type: "folder",
        children: [
            { name: "ReadMe.md", type: "file" },
            { name: "main.py", type: "file" }
        ]
    }
];

// 2. Function to create the HTML for the tree
function createTree(data, container) {
    const ul = document.createElement('ul');
    ul.className = 'tree-list';

    data.forEach(item => {
        const li = document.createElement('li');
        
        // Create the row item
        const itemDiv = document.createElement('div');
        itemDiv.className = 'tree-item';
        
        // Add icons based on type
        const icon = item.type === 'folder' ? '📁' : '- 📄';
        itemDiv.innerHTML = `<span class="chevron">${icon}</span> <span>${item.name}</span>`;

        li.appendChild(itemDiv);

        // If it's a folder, handle children and click events
        if (item.type === 'folder' && item.children) {
            const nestedUl = document.createElement('div');
            nestedUl.className = 'nested active'; // 'active' makes it open by default
            createTree(item.children, nestedUl);
            li.appendChild(nestedUl);

            // Toggle logic
            itemDiv.addEventListener('click', () => {
                nestedUl.classList.toggle('active');
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
window.onclick = function(event) {
    if (!event.target.matches('.nav-btn')) {
        const dropdowns = document.getElementsByClassName("dropdown-content");
        for (let i = 0; i < dropdowns.length; i++) {
            dropdowns[i].classList.remove('show');
        }
    }
}