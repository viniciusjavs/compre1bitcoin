function timestamp() {
    return Math.round(new Date().getTime()/1000.0)
}

function update_values() {
    $.getJSON($SCRIPT_ROOT+"/api/btc?"+timestamp(),
	      function(data) {
		  $("#btc").text(data.btc)
	      });
}

setInterval(update_values, 30000);
