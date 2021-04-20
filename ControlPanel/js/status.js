$(document).ready(function(){

			setInterval(getStatus("http://192.168.1.4:5002/heartBeat", "#statusText small", setBackgroundColor, '#324C5C'), 3000);
			setInterval(getStatus("http://192.168.1.4:5002/water/heartBeat", "#waterText small", null, null), 3000);
			setInterval(getStatus("http://192.168.1.4:5002/lux/heartBeat", "#moistureText small", null, null), 3000);
			setInterval(getStatus("http://192.168.1.4:5002/moisture/heartBeat", "#luxText small",  null, null), 3000);
			setInterval(getStatus("http://192.168.1.4:5002/temp/heartBeat", "#tempText small",  null, null), 3000);

			$("#shutdownButton").click(function() {
				var xhttp = new XMLHttpRequest();
				xhttp.onreadystatechange = function() {
					if (this.readyState == 4 && this.status == 200) {
						alert("Garden Shutdown Complete");
					}
				}
				xhttp.open("GET", "http://192.168.1.4:5002/shutdown", true);
				xhttp.send();
			});
		});

function setBackgroundColor(color) {
	$("body").css('background-color', color);
}

function getModuleStatus(url, element) {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200 && this.response == "True") {
			$(element).text("ON");
			$(element).css("font-weight", "Bold");
			$(element).removeClass("text-danger");
			$(element).addClass("text-success");
			$("body").css('background-color', 'white');
		} else if(this.readyState == 4 && this.status == 0){
			$(element).text("OFF");
			$(element).css("font-weight", "Bold");
			$(element).removeClass("text-success");
			$(element).addClass("text-danger");
		}
	}
	xhttp.open("GET", url, true);
	xhttp.send();
}

function getStatus(url, element, callback, arg) {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200 && this.response === "ok") {
			$(element).text("ON");
			$(element).css("font-weight", "Bold");
			$(element).removeClass("text-danger");
			$(element).addClass("text-success");
			$("body").css('background-color', 'white');
		} else if(this.readyState == 4 && this.status == 0){
			$(element).text("OFF");
			$(element).css("font-weight", "Bold");
			$(element).removeClass("text-success");
			$(element).addClass("text-danger");
			if(callback != null){
				callback(arg);
			}
		}
	}
	xhttp.open("GET", url, true);
	xhttp.send();
}