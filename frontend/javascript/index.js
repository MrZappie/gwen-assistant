async function onSelectClick(params) {
    const data = null

    const result = await fetch("http://127.0.0.1:8000/api/selectdir");
    data = await result.json();
    console.log(data)
}