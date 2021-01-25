		$(document).ready(function(){

				var makeItRain = function() {
	//clear out everything
	$(".rain").empty();

	var increment = 0;
	var drops = "";
	var backDrops = "";

	while (increment < 100) {
		//couple random numbers to use for various randomizations
		//random number between 98 and 1
		var randoHundo = Math.floor(Math.random() * (98 - 1 + 1) + 1);
		//random number between 5 and 2
		var randoFiver = Math.floor(Math.random() * (5 - 2 + 1) + 2);
		//increment
		increment += randoFiver;
		//add in a new raindrop with various randomizations to certain CSS properties
		drops +=
		'<div class="drop" style="left: ' +
		increment +
		"%; bottom: " +
		(randoFiver + randoFiver - 1 + 100) +
		"%; animation-delay: 0." +
		randoHundo +
		"s; animation-duration: 0.5" +
		randoHundo +
		's;"><div class="stem" style="animation-delay: 0.' +
		randoHundo +
		"s; animation-duration: 0.5" +
		randoHundo +
		's;"></div><div class="splat" style="animation-delay: 0.' +
		randoHundo +
		"s; animation-duration: 0.5" +
		randoHundo +
		's;"></div></div>';
		backDrops +=
		'<div class="drop" style="right: ' +
		increment +
		"%; bottom: " +
		(randoFiver + randoFiver - 1 + 100) +
		"%; animation-delay: 0." +
		randoHundo +
		"s; animation-duration: 0.5" +
		randoHundo +
		's;"><div class="stem" style="animation-delay: 0.' +
		randoHundo +
		"s; animation-duration: 0.5" +
		randoHundo +
		's;"></div><div class="splat" style="animation-delay: 0.' +
		randoHundo +
		"s; animation-duration: 0.5" +
		randoHundo +
		's;"></div></div>';
	}

	$(".rain.front-row").append(drops);
	$(".rain.back-row").append(backDrops);
	};

	$(".splat-toggle.toggle").on("click", function() {
	$("body").toggleClass("splat-toggle");
	$(".splat-toggle.toggle").toggleClass("active");
	makeItRain();
	});

	$(".back-row-toggle.toggle").on("click", function() {
	$("body").toggleClass("back-row-toggle");
	$(".back-row-toggle.toggle").toggleClass("active");
	makeItRain();
	});

	$(".single-toggle.toggle").on("click", function() {
	$("body").toggleClass("single-toggle");
	$(".single-toggle.toggle").toggleClass("active");
	makeItRain();
	});

	makeItRain();

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

			$("#runButton").click(function() {
				var runTime = parseInt($('#runInput').val());
				if(!isNaN(runTime)) {
					console.log("Watering plants for " + runTime + " seconds.");
					xhttp.onreadystatechange = function() {
						if(this.readyState == 4 && this.status == 200) {
							console.log("watered plants.");
						}
					}
					xhttp.open("GET", "http://192.168.1.4/runPump/" + runTime, true);
					xhttp.send();
				}
			});

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
		});