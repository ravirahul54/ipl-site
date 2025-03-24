async function fetchSchedule() {
    const sheetID = "205719425";
    const url = `https://docs.google.com/spreadsheets/d/${sheetID}/gviz/tq?tqx=out:json`;

    const response = await fetch(url);
    const text = await response.text();
    const json = JSON.parse(text.substring(47).slice(0, -2));

    let table = document.getElementById("scheduleTable");
    json.table.rows.forEach(row => {
        let match = row.c.map(cell => cell ? cell.v : ""); 
        let tr = `<tr><td>${match[0]}</td><td>${match[1]}</td><td>${match[2]}</td></tr>`;
        table.innerHTML += tr;
    });
}

fetchSchedule();
