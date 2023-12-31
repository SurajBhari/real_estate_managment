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
    var advisor = document.getElementById("advisors").value;
    var month = document.getElementById("months").value;
    var download_button = document.getElementById("download");
    url = `/get_incentive/${month}/${advisor}`;
    // if there is only month then url 
    if(month!='' && advisor == ''){
        url = `/get_incentive/${month}`;
    }
    fetch(url)
            .then(response => response.text())
            .then(data => {
                data = JSON.parse(data);
                var table = document.getElementById("data");
                table.innerHTML = '';
                // iterate over data
                // plot_name is i[0]-i[1]-i[2]
                // advisor is i[3]
                // reciept date is i[4]
                // reciept ammount is i[5]
                let total_incentive = 0;
                let total_reciept_amount = 0;
                // table head, Plot, Advsior, Date of Reciept, Reciept Ammount, Incentive
                var row = document.createElement("tr");
                var plot_name_cell = document.createElement("th");
                var reciept_number_cell = document.createElement("th");
                var advisor_name_cell = document.createElement("th");
                var reciept_date_cell = document.createElement("th");
                var reciept_ammount_cell = document.createElement("th");
                var incentive_cell = document.createElement("th");
                var customer_name_cell = document.createElement("th");
                var is_emi_cell = document.createElement("th");

                plot_name_cell.innerHTML = 'Plot';
                reciept_number_cell.innerHTML = 'Reciept No.';
                reciept_date_cell.innerHTML = 'Date of Reciept';
                reciept_ammount_cell.innerHTML = 'Reciept Ammount';
                advisor_name_cell.innerHTML = 'Advisor';
                customer_name_cell.innerHTML = 'Customer';
                is_emi_cell.innerHTML = "EMI";

                incentive_cell.innerHTML = 'Incentive';

                row.appendChild(plot_name_cell);
                row.appendChild(reciept_number_cell);
                row.appendChild(reciept_date_cell);
                row.appendChild(reciept_ammount_cell);
                row.appendChild(advisor_name_cell);
                row.appendChild(customer_name_cell);
                row.appendChild(incentive_cell);
                row.appendChild(is_emi_cell);
                table.appendChild(row);
                for(let i=0; i< data[0].length; i++) {
                    /*
                    [
                    project,
                    sector,
                    plot,
                    reciept_no,
                    adv,
                    reciept['date'],
                    reciept['amount'],
                    incentive,
                    incentive_percent,
                    is_emi
                    ]*/
                    var plot_name = data[0][i][0] + '-' + data[0][i][1] + '-' + data[0][i][2];
                    var reciept_no = data[0][i][3];
                    var advisor_name = data[0][i][4];
                    var customer_name = data[0][i][5];
                    var reciept_date = data[0][i][6];
                    var reciept_ammount = data[0][i][7];      
                    var incentive = data[0][i][8];
                    var incentive_percent = data[0][i][9]; 
                    var is_emi = data[0][i][10];   
                    total_reciept_amount += reciept_ammount;
                    total_incentive += incentive;
                    // series should be in the same order as the table head
                    // plot, reciept number, reciept date, reciept ammount, advisor, incentive
                    var row = document.createElement("tr");
                    var plot_name_cell = document.createElement("td");
                    var reciept_number_cell = document.createElement("td");
                    var advisor_name_cell = document.createElement("td");
                    var reciept_date_cell = document.createElement("td");
                    var reciept_ammount_cell = document.createElement("td");
                    var incentive_cell = document.createElement("td");
                    var customer_name_cell = document.createElement("td");
                    var is_emi_cell = document.createElement("td");

                    is_emi_cell.innerHTML = is_emi;
                    plot_name_cell.innerHTML = plot_name;
                    reciept_number_cell.innerHTML = reciept_no;
                    advisor_name_cell.innerHTML = advisor_name;
                    reciept_date_cell.innerHTML = reciept_date;
                    reciept_ammount_cell.innerHTML = `₹ ${reciept_ammount}`;
                    customer_name_cell.innerHTML = customer_name;
                    incentive_cell.innerHTML = `₹ ${reciept_ammount} X ${incentive_percent}% = ₹ ${incentive}`;

                    row.appendChild(plot_name_cell);
                    row.appendChild(reciept_number_cell);
                    row.appendChild(reciept_date_cell);
                    row.appendChild(reciept_ammount_cell);
                    row.appendChild(advisor_name_cell);
                    row.appendChild(customer_name_cell);
                    row.appendChild(incentive_cell);
                    row.appendChild(is_emi_cell);
                    table.appendChild(row);
                }
                var row = document.createElement("tr");
                var total_incentive_cell = document.createElement("td");
                total_incentive_cell.innerHTML = `₹ ${total_incentive}`;
                // add 6 empty td
                row.appendChild(document.createElement("td"));
                row.appendChild(document.createElement("td"));
                row.appendChild(document.createElement("td"));

                var total_reciept_amount_cell = document.createElement("td");
                total_reciept_amount_cell.innerHTML = `₹ ${total_reciept_amount}`;
                row.appendChild(total_reciept_amount_cell);
                row.appendChild(document.createElement("td"));
                row.appendChild(document.createElement("td"));

                row.appendChild(total_incentive_cell);
                table.appendChild(row);
                // set table text color to green
                table.style.color = 'green';
                
                total_incentive = 0;
                total_reciept_amount = 0;

                var table = document.getElementById("uncollected");
                table.innerHTML = '';
                // table head, Plot, Advsior, Date of Reciept, Reciept Ammount, Incentive
                var row = document.createElement("tr");
                var plot_name_cell = document.createElement("th");
                var reciept_number_cell = document.createElement("th");
                var advisor_name_cell = document.createElement("th");
                var reciept_date_cell = document.createElement("th");
                var reciept_ammount_cell = document.createElement("th");
                var incentive_cell = document.createElement("th");
                var customer_name_cell = document.createElement("th");
                var is_emi_cell = document.createElement("th");

                plot_name_cell.innerHTML = 'Plot';
                reciept_date_cell.innerHTML = 'Date of Reciept';
                reciept_ammount_cell.innerHTML = 'Kisht Ammount';
                advisor_name_cell.innerHTML = 'Advisor';
                incentive_cell.innerHTML = 'Incentive';
                customer_name_cell.innerHTML = 'Customer';
                is_emi_cell.innerHTML = 'EMI';
                
                row.appendChild(plot_name_cell);
                row.appendChild(reciept_date_cell);
                row.appendChild(reciept_ammount_cell);
                row.appendChild(advisor_name_cell);
                row.appendChild(customer_name_cell);
                row.appendChild(incentive_cell);
                row.appendChild(is_emi_cell);

                table.appendChild(row);
                
                for(let i=0; i< data[1].length; i++) {
                    /*[
                        project,
                        sector,
                        plot,
                        adv,
                        x.strftime("%Y-%m-%d"),
                        kisht,
                        incentive,
                        incentive_percent,
                        is_emi
                        ]*/
                    var plot_name = data[1][i][0] + '-' + data[1][i][1] + '-' + data[1][i][2];
                    var advisor_name = data[1][i][3];
                    var customer_name = data[1][i][4];
                    var reciept_date = data[1][i][5];
                    var reciept_ammount = data[1][i][6];
                    var incentive = data[1][i][7];     
                    var incentive_percent = data[1][i][8];
                    var is_emi = data[1][i][9];

                    total_incentive += incentive;
                    total_reciept_amount += reciept_ammount;

                    // series should be in the same order as the table head
                    // plot, reciept date, reciept ammount, advisor, incentive
                    var row = document.createElement("tr");
                    
                    var is_emi_cell = document.createElement("td");
                    var plot_name_cell = document.createElement("td");
                    var reciept_date_cell = document.createElement("td");
                    var reciept_ammount_cell = document.createElement("td");
                    var advisor_name_cell = document.createElement("td");
                    var customer_name_cell = document.createElement("td");
                    var incentive_cell = document.createElement("td");

                    is_emi_cell.innerHTML = is_emi;
                    plot_name_cell.innerHTML = plot_name;
                    reciept_date_cell.innerHTML = reciept_date;
                    reciept_ammount_cell.innerHTML = `₹ ${reciept_ammount}`;
                    advisor_name_cell.innerHTML = advisor_name;
                    customer_name_cell.innerHTML = customer_name;
                    incentive_cell.innerHTML = `₹ ${reciept_ammount} X ${incentive_percent}% = ₹ ${incentive}`;

                    row.appendChild(plot_name_cell);
                    row.appendChild(reciept_date_cell);
                    row.appendChild(reciept_ammount_cell);
                    row.appendChild(advisor_name_cell);
                    row.appendChild(customer_name_cell);
                    row.appendChild(incentive_cell);
                    row.appendChild(is_emi_cell);
                    table.appendChild(row);
                }
                var row = document.createElement("tr");
                var total_incentive_cell = document.createElement("td");
                total_incentive_cell.innerHTML = `₹ ${total_incentive}`;
                // add 2 empty td
                row.appendChild(document.createElement("td"));
                row.appendChild(document.createElement("td"));

                var total_reciept_amount_cell = document.createElement("td");
                total_reciept_amount_cell.innerHTML = `₹ ${total_reciept_amount}`;
                row.appendChild(total_reciept_amount_cell);

                // add 2 empty td
                row.appendChild(document.createElement("td"));
                row.appendChild(document.createElement("td"));

                row.appendChild(total_incentive_cell);
                table.appendChild(row);
                table.style.color = 'red';
            })
            .catch(error => console.error('Error fetching data from the backend:', error));            
}
doMagic();