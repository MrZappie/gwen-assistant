// home-file.js

export async function fetchFolder(path) {
    const res = await fetch(`/api/open_folder/${encodeURIComponent(path)}`);
    const data = await res.json();

    if (data.error) {
        throw new Error(data.message);
    }

    return data.children;
}

export async function fetchFile(path) {
    const res = await fetch(`/api/get_file_content/${encodeURIComponent(path)}`, {
        method: "POST"
    });

    return res.json();
}
