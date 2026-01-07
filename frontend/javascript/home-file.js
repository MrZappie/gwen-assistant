export async function fetchFolder(path = "") {
    const res = await fetch(`/api/open_folder?path=${encodeURIComponent(path)}`);
    const data = await res.json();
    return data.children;
}

export async function fetchFile(path) {
    const res = await fetch(`/api/get_file_content?path=${encodeURIComponent(path)}`);
    return res.json();
}
