var client_id = Date.now()
document.querySelector("#ws-id").textContent = client_id;
var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
var peekContent
ws.onmessage = function(event) {
    // TODO: get site list from here and append to it
    var content = document.createTextNode(event.data)
    let sites = content
    let statuses = content
    peekContent = content           
};
function sendMessage(event) {
    var input = document.getElementById("messageText")
    ws.send(input.value)
    input.value = ''
    event.preventDefault()
}