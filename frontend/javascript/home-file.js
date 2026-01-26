export async function fetchFolder(path = "") {
    const res = await fetch(`/api/open_folder?path=${encodeURIComponent(path)}`);
    const data = await res.json();
    return data.children;
}

export async function fetchFile(path) {
    const res = await fetch(`/api/get_file_content?path=${encodeURIComponent(path)}`);
    return res.json();
}

export async function saveFile(path, content) {
    const response = await fetch("/api/save-file", {
        method: "POST", 
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ path, content }),
    });

    if (!response.ok) {
        throw new Error("Failed to save file");
    }

    return await response.json();
}