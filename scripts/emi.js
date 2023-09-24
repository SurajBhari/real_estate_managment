function exportData(){
    // get data that is presented in table 
    let tables = [document.getElementById('data'), document.getElementById('uncollected')];
    let dataTo = {
        headers: [],
        data: []
    }
    for (let table of tables) {
        let data = [];
        let headers = [];

        for(let i=0; i<table.rows.length; i++) {
            let tableRow = table.rows[i];
            let rowData = [];
            for(let j=0; j<tableRow.cells.length; j++) {
                if (i === 0) {
                    headers.push(tableRow.cells[j].innerHTML);
                } else if (i  === 1){
                    let cell = tableRow.cells[j];
                    if(cell.querySelector('select')){
                        let tc = tableRow.cells[j].querySelector('select').options[tableRow.cells[j].querySelector('select').selectedIndex].textContent;
                        rowData.push(tc);
                    }
                    else{
                        rowData.push(tableRow.cells[j].innerHTML);
                    }
                } else {
                    rowData.push(tableRow.cells[j].innerHTML);
                }
            }
            data.push(rowData);
        }
        dataTo.headers.push(headers);
        dataTo.data.push(data);
    }
    // make a POST request to the backend to export the data
    const url = '/export';
    const dataToSend = dataTo;  
    // first POST to the url store the response and alert
    fetch(url, {
        method: 'POST',
        body: JSON.stringify(dataToSend),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.text())
    .then(data => {
        console.log(data);
        alert(data);
    })

}

function doMagic(){
    const project_element = document.getElementById("project"); 
    const month_element = document.getElementById("month");
    const project = project_element.options[project_element.selectedIndex].value;
    const month = month_element.options[month_element.selectedIndex].value;
    const url = `/get_month_emi/${month}/${project}`;
    fetch(url)
            .then(response => response.text())
            .then(data => {
                data = JSON.parse(data);
                var table = document.getElementById("data");
                table.innerHTML = '';
                // table heads  = project-sector-plot, reciept_number, customer_name, date_of_reciept, reciept_ammount, emi_ammount, advisor
                var row = document.createElement("tr");
                var cell = document.createElement("th");
                cell.innerHTML = "Project-Sector-Plot";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Reciept Number";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Customer Name";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Date of Reciept";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Reciept Amount";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Remaining Amount";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Advisor";
                row.appendChild(cell);
                table.appendChild(row);
                for(let i=0; i<data[0].length; i++){
                    let elem = data[0][i];
                    if(project_element.value != '0'){
                        if(project_element.value != elem[0]){
                            continue;
                        }
                    }
                    row = document.createElement("tr");
                    cell = document.createElement("td");
                    cell.innerHTML = elem[0]+"-"+elem[1]+"-"+elem[2];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[3];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[4];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[5];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[6];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[7];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[8];
                    row.appendChild(cell);
                    table.appendChild(row);
                }
                table.style.color = "green";
                // uncollected emi
                table = document.getElementById("uncollected");
                table.innerHTML = '';
                table.style.color = "red";
                // headds are project-sector-plot, customer_name, date_of_emi, kisht, emi_ammount, advisor
                row = document.createElement("tr");
                cell = document.createElement("th");
                cell.innerHTML = "Project-Sector-Plot";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Customer Name";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Date of EMI";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Collected";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Remaining Amount";
                row.appendChild(cell);
                cell = document.createElement("th");
                cell.innerHTML = "Advisor";
                row.appendChild(cell);
                table.appendChild(row);
                for(let i=0; i<data[1].length; i++){
                    let elem = data[1][i];
                    if(project_element.value != '0'){
                        if(project_element.value != elem[0]){
                            continue;
                        }
                    }
                    row = document.createElement("tr");
                    cell = document.createElement("td");
                    cell.innerHTML = elem[0]+"-"+elem[1]+"-"+elem[2];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[3];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[4];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[5];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[6];
                    row.appendChild(cell);
                    cell = document.createElement("td");
                    cell.innerHTML = elem[7];
                    row.appendChild(cell);
                    table.appendChild(row);
                }
            })
            .catch(error => console.error('Error fetching data from the backend:', error));            
}