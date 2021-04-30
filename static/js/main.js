var addSiteBtn = document.getElementById('addNeWebsite');
var addSiteDialog = document.getElementById('add-website');
var outputBox = document.querySelector('output');
var saveBtn = document.getElementById('saveBtn');
var siteData;
let editSiteDialog = document.getElementById("edit-website");
const hostname = "127.0.0.1:8000";

// fuction to upload the website entered in the modal form
function saveWebsite(event){
  let url = "/addsite"
  const siteName = document.getElementById("sitename");
  const siteUrl = document.getElementById("website-url");
  const siteProtocol = document.getElementById("site-protocol");
  const sitePort = document.getElementById("website-port");
  const website = { 
  	name: siteName.value,
  	protocol: siteProtocol.value,
  	url: siteUrl.value,
  	port: sitePort.value,
  };
  siteData = website;
  // upload form data
  fetch(url, {
    method: "POST",
    body: JSON.stringify(website),
    headers: {"Content-type": "application/json; charset=UTF-8"}
  })
  .then(response => response.json)
  .then(json => console.log(json()))
  .catch(err => alert("Failed to add site"));
}

// function to upload modifications to a site
function modifyWebsite(event){
	// TODO: get website from event or whatever and use it to get values from it
	let siteID;
	let url = `/update/${siteID}`;
	const website = {};

	// TODO: complete this
	fetch(url, {
		method: "UPDATE",
		body: JSON.stringify(website),
		headers: {"Content-type": "application/json; charset=UTF-8"}
	});
}

// "Add new website" button opens the <dialog> modally
addSiteBtn.addEventListener('click', function onOpen() {
  if (typeof addSiteDialog.showModal === "function") {
    addSiteDialog.showModal();
  } else {
    alert("The <dialog> API is not supported by this browser, please download the latest version of Chrome, Firefox, or Edge");
  }
});
// "Confirm" button of form triggers "close" on dialog because of [method="dialog"]
addSiteDialog.addEventListener('close', function onClose() {
  // TODO: do something when it closes Probably a toast, snackbar, or aleart
  outputBox.value = addSiteDialog.returnValue + " button clicked - " + (new Date()).toString();
});
// "save" button saves a website and uploads a fetch
saveBtn.addEventListener('click', saveWebsite);
