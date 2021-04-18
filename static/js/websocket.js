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

document.querySelector("#ws-id").textContent = client_id;
var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`); // websocket for coms
var peekContent; // debug var

// Function to send data via the socket
function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}
// Function to delete a site given id
function deleteSite(id){
    // TODO: modify variable then table
    let deleted_site = websites.splice(id, 1);
}

// Function to update a site given the data
function updateSite(site){
    // TODO: modify variable then table
    websites[site.id] = site
}
// function to refresh the site list
function refreshSites(sites){
    // TODO: modify variable then table
    websites = sites;
}
// funtion to add a website
function createSite(site){
    // TODO: add to variable then data table
    websites.push(site);
}

// actions to perform when a message is recieved via the websocket
ws.onmessage = function(event) {
    // TODO: get site list from here and append to it
    var content = JSON.parse(event.data);
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

    let sites = content;
    let statuses = content;
    peekContent = content;
    console.log(`recieved ${content[0]}`)        
};