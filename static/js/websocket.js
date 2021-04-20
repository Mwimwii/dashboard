var client_id = Date.now();
var websites = []; // array of websites

// Enum of actions
const actions = {
    REFRESH: 0,
    UPDATE: 2,
    DELETE: 2,
    CREATE: 3,
};
Object.freeze(actions);
var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`); // websocket for coms
var peekContent; // debug var

// Function to send data via the socket
function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}

// Function to set values of a row
function setRowValues(site, row){
    // insert cells at row end
    let siteName = row.insertCell();
    let protocol = row.insertCell();
    let url= row.insertCell();
    let port = row.insertCell();
    let lastCheck = row.insertCell();
    let serverStat = row.insertCell();
    let siteStat = row.insertCell();
    // add text to cell
    let text = document.createTextNode(site.name);
    siteName.appendChild(text);
    text.nodeValue = site.protocol;
    protocol.appendChild(text);
    text.nodeValue = site.url;
    url.appendChild(text);
    text.nodeValue = site.port;
    port.appendChild(text);
    text.nodeValue = site.timestamp;
    lastCheck.appendChild(text)
    text.nodeValue = site.online;
    serverStat.appendChild(text);
    text.nodeValue = site.response_code;
    siteStat.appendChild(text);
}

// Function to add rows to the table
function addRow(site){
    // get body reference
    let tbody = document.getElementById("sites-table-body");
    // insert a row at the end of the table
    let trow = tbody.insertRow();
    // set an id for the row
    trow.setAttribute("id", site.id);
    let i = websites.length
    if(i % 2 == 0){
        trow.className = "even";
    } else{
        trow.className = "odd";
    }
    // set values of the row according to the site values
    setRowValues(site, trow);
}

// Function to delete a site given id
function deleteSite(id){
    // modify variable
    let deleted_site = websites.splice(id, 1);
    // get the row by row id (which is site id)
    let trow = document.getElementById(id);
    // remove the row from the table body
    trow.parentNode.removeChild(row);
}

// Function to update a site given the data
function updateSite(site){
    // modify variable
    const siteExists = (element) => element.id === site.id;
    let website = websites.find(siteExists);
    if(typeof website !== "undefined"){
        let index = websites.findIndex(siteExists);
        websites[index] = site;
        let trow = document.getElementById(site.id);
        setRowValues(site, trow);
    }
}
// function to refresh the site list
function refreshSites(sites){
    // modify variable then table
    websites = [];
    for(let i = 0; i < sites.length; i++){
        // get site at index i
        let site = sites[i];
        // add site to websites array
        // when websites is empty the row is colored even, then the site added to websites
        addRow(site);
        // add site to websites array
        websites.push(site);
    }
}
// funtion to add a website
function createSite(site){
    // add to variable then data table
    websites.push(site);
    addRow(site);
}

// actions to perform when a message is recieved via the websocket
ws.onmessage = function(event) {
    // TODO: get site list from here and append to it
    let content = JSON.parse(event.data);
    switch(content.action){
        case actions.REFRESH:
            refreshSites(content.data)
            break;
        case actions.UPDATE:
            updateSite(content.data)
            break;
        case actions.DELETE:
            deleteSite(content.data)
            break;
        case actions.CREATE:
            createSite(content.data)
            break;
    }
    peekContent = content;
    // TODO: remove pre production
    console.log(`recieved ${content}`)        
};