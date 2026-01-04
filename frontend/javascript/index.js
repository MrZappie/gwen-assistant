// index.js
const selectBtn = document.getElementById('select-project-btn');

if (selectBtn) { // Added a check to prevent errors
    selectBtn.addEventListener('click', () => {
        const dummyData = {
            status: "success",
            folder_name: "My_New_Project",
            files: ["main.py", "data.csv", "README.md"]
        };

        localStorage.setItem('selectedProject', JSON.stringify(dummyData));

        // Opens in a new tab
        window.open('home.html', '_blank'); 
    });
}