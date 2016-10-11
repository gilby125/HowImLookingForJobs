// This chunk of code is used along with phantomjs to
// return javascript interpreted pages to other
// processes through a websocket.

//
// Author: Alan LE MOUROUX
// Date: 05/10/2016
//

var serversocket = new WebSocket('ws://127.0.0.1:8002/');

serversocket.onopen = function() {
    serversocket.send('ok')
    console.log("Hello, ready to serve !")
}

// Returns a page when receiving an url
serversocket.onmessage = function(e) {
    console.log("\n" + Date().toLocaleString() + ": " + e.data)
    var page = require('webpage').create();
    if (e.data == 'done') {
	phantom.exit();
    }
    settings = {
	operation: 'GET',
	encoding: 'utf8'
    };
    page.open(encodeURI(e.data), settings, function() {
	serversocket.send(page.content);
    });
};

serversocket.onerror = function(e) {
    console.log(e);
    phantom.exit();
};

serversocket.onclose = function() {
    console.log("\nbye bye !");
    phantom.exit();
}
