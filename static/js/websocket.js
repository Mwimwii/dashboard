var client_id = Date.now();
var websites = []; // array of websites

// Enum of actions
const actions = {
    REFRESH: 0,
    UPDATE: 1,
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
function setRowValues(site){
    // create IDs for the cells
    let nameID = `siteName${site.id}`;
    let protoID = `siteprotocol${site.id}`;
    let urID = `siteUrl${site.id}`;
    let portID = `sitePort${site.id}`;
    let lastCheckID = `siteTimestamp${site.id}`;
    let servestaID = `siteServerStatus${site.id}`;
    let sitestatID = `siteResponseCode${site.id}`;
    // get cell rows
    let siteName = document.getElementById(nameID);
    let protocol = document.getElementById(protoID);
    let url= document.getElementById(urID);
    let port = document.getElementById(portID);
    let lastCheck = document.getElementById(lastCheckID);
    let serverStat = document.getElementById(servestaID);
    let siteStat = document.getElementById(sitestatID);
    // make the site url a link
    siteurl = `<a href="${site.protocol}://${site.url}:${site.port}" target="_blank">${site.url}</a>`
    // add text to cell
    siteName.innerHTML = site.name
    protocol.innerHTML = site.protocol;
    url.innerHTML = siteurl;
    port.innerHTML = site.port;
    lastCheck.innerHTML = site.timestamp;
    serverStat.innerHTML = site.online;
    siteStat.innerHTML = site.response_code;
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
    // insert cells to the row
    let siteName = trow.insertCell();
    let protocol = trow.insertCell();
    let url= trow.insertCell();
    let port = trow.insertCell();
    let lastCheck = trow.insertCell();
    let serverStat = trow.insertCell();
    let siteStat = trow.insertCell();
    // create IDs for the cells
    let nameID = `siteName${site.id}`;
    let protoID = `siteprotocol${site.id}`;
    let urID = `siteUrl${site.id}`;
    let portID = `sitePort${site.id}`;
    let lastCheckID = `siteTimestamp${site.id}`;
    let servestaID = `siteServerStatus${site.id}`;
    let sitestatID = `siteResponseCode${site.id}`;
    // set IDs for the cells
    siteName.setAttribute("id", nameID);
    protocol.setAttribute("id", protoID);
    url.setAttribute("id", urID);
    port.setAttribute("id", portID);
    lastCheck.setAttribute("id", lastCheckID);
    serverStat.setAttribute("id", servestaID);
    siteStat.setAttribute("id", sitestatID);
    // set values of the row according to the site values
    setRowValues(site);
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
    msg = `found site:\nName: ${website.name} in array\n${website}`
    console.log(msg)
    if(typeof website !== "undefined"){
        let index = websites.findIndex(siteExists);
        websites[index] = site;
        setRowValues(website);
        msg = `updating site:\nName: ${website.name}`
        console.log(msg)
    }
}
// function to refresh the site list
function refreshSites(sites){
    // modify variable then table
    websites = [];
    tbody = document.getElementById("sites-table-body");
    // delete old rows from table
    let numRows = tbody.rows.length;
    for(let i = 0; i < numRows; i++){
        tbody.deleteRow(i)
    }
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
    console.log(`recieved:\n ${content}`)        
};

ws.onclose = function(event) {
    console.log("web socket disconnected for some reason");
    console.log("reason:");
    console.log(event);
    console.log(event.data);
    ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`); // try to reconnect
}