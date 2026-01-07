async function onSelectClick(params) {
    const result = await fetch("http://127.0.0.1:8000/api/selectdir");
    const data = await result.json();

    if (data['error'] === true) {
        
    }else {
        window.location.replace("/home.html");
        console.log("[TEST]");
        console.log(data);
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    try {
        const res = await fetch("http://127.0.0.1:8000/api/project-status");
        const data = await res.json();
        
        if (data.has_project_directory) {
            window.location.replace("home.html");
        }
    } catch (err) {
        console.error("Backend not reachable", err);
    }
});