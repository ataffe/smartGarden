$(document).ready(function(){

			setInterval(getStatus("http://192.168.1.4:5002/heartBeat", "#statusText small", setBackgroundColor, '#324C5C'), 1000);
			setInterval(getModuleStatus("http://192.168.1.4:5002/water/heartBeat", "#waterText", null, null), 1000);
			setInterval(getModuleStatus("http://192.168.1.4:5002/lux/heartBeat", "#moistureText", null, null), 1000);
			setInterval(getModuleStatus("http://192.168.1.4:5002/moisture/heartBeat", "#luxText",  null, null), 1000);
			setInterval(getModuleStatus("http://192.168.1.4:5002/temp/heartBeat", "#tempText",  null, null), 1000);

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
		if (this.readyState == 4 && this.status == 200 && this.response === "True") {
			console.log("success for element: " + element);
			$(element).text("ON");
			$(element).removeClass("badge badge-warning");
			$(element).removeClass("badge badge-danger");
			$(element).addClass("badge badge-success");
		} else if(this.readyState == 4 && (this.response === "False" || this.status == 0)){
			$(element).text("OFF");
			$(element).removeClass("badge badge-warning");
			$(element).removeClass("badge badge-success");
			$(element).addClass("badge badge-danger");
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
			$(element).removeClass("text-warning");
			$(element).removeClass("text-danger");
			$(element).addClass("text-success");
			$("body").css('background-color', 'white');

			$("#shutdownButton").removeClass("disabled");
			$("#shutdownButton").prop("disabled", false);
		} else if(this.readyState == 4 && this.status == 0){
			$(element).text("OFF");
			$(element).css("font-weight", "Bold");
			$(element).removeClass("text-warning");
			$(element).removeClass("text-success");
			$(element).addClass("text-danger");

			$("#shutdownButton").addClass("disabled");
			$("#shutdownButton").prop("disabled", true);
			if(callback != null){
				callback(arg);
			}
		}
	}
	xhttp.open("GET", url, true);
	xhttp.send();
}