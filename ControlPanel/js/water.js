		$(document).ready(function(){
			var xhttp = new XMLHttpRequest();
			xhttp.onreadystatechange = function() {
				if(this.readyState == 4 && this.status == 200) {
					console.log("Received new water interval");
					$("#currentWaterLabel span strong").text(this.response);
				}
			}
			xhttp.open("GET", "http://192.168.1.4:5002/getWater", true);
			xhttp.send();

			$(document).on("click", "a", function() {
				$('#dropdownMenuButton').html($(this).text());
			});

			function alertTimeout(wait){
				setTimeout(function(){
					$('#selectAlert').children('.alert:first-child').alert('close');
				}, wait);
			}

			$("#setButton").click(function() {
				var hoursString = $('#dropdownMenuButton').html().split(" ")[0];
				var hours = parseInt(hoursString, 10);
				if(!isNaN(hours)) {
					xhttp.onreadystatechange = function() {
						if(this.readyState == 4 && this.status == 200 && this.response == "ok") {
							console.log("Set water interval successfully");
							xhttp.open("GET", "http://192.168.1.4:5002/getWater", true);
							xhttp.send();
							$('#selectAlert').children('.alert:first-child').alert('close');
							$("#selectAlert").append("<div class='alert alert-success alert-dismissable' role='alert' id='myAlert2'> <button type='button' class='close' data-dismiss='alert'  aria-hidden='true'>&times;</button>New water interval successfully set!</div>");
							alertTimeout(2000);
						} else if(this.readyState == 4 && this.status == 200) {
							console.log("Received new water interval");
							$("#currentWaterLabel span mark").text(this.response);
						}
					}
					xhttp.open("GET", "http://192.168.1.4:5002/setWater/" +  hours, true);
					xhttp.send();
				} else {
					$('#selectAlert').children('.alert:first-child').alert('close');
					$("#selectAlert").append("<div class='alert alert-danger alert-dismissable' role='alert' id='myAlert2'> <button type='button' class='close' data-dismiss='alert'  aria-hidden='true'>&times;</button> Please select an interval.</div>");
					alertTimeout(2000);
				}
			});

			$("#runButton").click(function() {
				var runTime = parseInt($('#runInput').val());
				console.log("watering plants: " + runTime);
				if(!isNaN(runTime)) {
					console.log("Watering plants for " + runTime + " seconds.");
					$("#runButton").html("Watering");
					$("#runButton").prop('disabled', true);
					xhttp.onreadystatechange = function() {
						if(this.readyState == 4 && this.status == 200) {
							console.log("watered plants.");
							$("#runButton").html("Run");
							$("#runButton").prop('disabled', false);
						}
					}
					xhttp.open("GET", "http://192.168.1.4:5002/runPump/" + runTime, true);
					xhttp.send();
				}
			});
		});