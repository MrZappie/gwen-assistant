// Static project data
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

const treeContainer = document.getElementById('folder-tree');

// Function to create the HTML tree with animations and icons
function createTree(data, container) {
    const ul = document.createElement('ul');
    ul.className = 'tree-list';

    data.forEach(item => {
        const li = document.createElement('li');
        const itemDiv = document.createElement('div');
        itemDiv.className = 'tree-item';

        const iconSpan = document.createElement('span');
        iconSpan.className = 'tree-icon';

        if (item.type !== 'file') {
            itemDiv.appendChild(iconSpan);
        }

        const textSpan = document.createElement('span');
        textSpan.textContent = item.name;

        itemDiv.appendChild(textSpan);
        li.appendChild(itemDiv);

        if (item.type === 'folder' && item.children) {
            const nestedUl = document.createElement('div');
            nestedUl.className = 'nested active';

            itemDiv.classList.add('open');

            createTree(item.children, nestedUl);
            li.appendChild(nestedUl);

            itemDiv.addEventListener('click', () => {
                nestedUl.classList.toggle('active');
                itemDiv.classList.toggle('open');
            });
        }

        ul.appendChild(li);
    });

    container.appendChild(ul);
}

// Initialize the tree on page load
document.addEventListener('DOMContentLoaded', () => {
    createTree(projectData, treeContainer);
});

// Dropdown Menu Logic
function toggleDropdown(id) {
    const dropdowns = document.getElementsByClassName("dropdown-content");
    for (let i = 0; i < dropdowns.length; i++) {
        if (dropdowns[i].id !== id) {
            dropdowns[i].classList.remove('show');
        }
    }
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
};
