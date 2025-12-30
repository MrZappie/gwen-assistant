const selectBtn = document.getElementById('select-project-btn');

selectBtn.addEventListener('click', async () => {
    try {
        // 1. Call your Python Flask server
        const response = await fetch('http://127.0.0.1:5000/select-folder');
        const data = await response.json();

        if (data.status === "success") {
            // 2. Store the folder name and files in localStorage
            localStorage.setItem('selectedProject', JSON.stringify(data));
            
            // 3. Open home.html in a new tab
            window.open('home.html', '_blank');
        } else if (data.status === "cancelled") {
            console.log("Selection cancelled by user.");
        }
    } catch (error) {
        alert("Make sure your app.py is running!");
        console.error("Error:", error);
    }
});