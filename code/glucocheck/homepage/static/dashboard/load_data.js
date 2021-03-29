/*import "https://code.highcharts.com/highcharts.js";
import "https://code.highcharts.com/highcharts-more.js";
import "https://code.highcharts.com/modules/solid-gauge.js";
*/
function returnFormattedDate(date) {
	/*
	* Returns the date in YYYY-MM-DD format (iso format).
	*
	* @param {array} date - the date with year, month, and day in different array positions.
	* 
	* @return {string} the date as a string in YYYY-MM-DD format.
	*/
	date = date.trim();
	date = date.split(" ");
	if (date[0] == "January") {
		date[0] = "01";
	}
	else if (date[0] == "February") {
		date[0] = "02";
	}
	else if (date[0] == "March") {
		date[0] = "03";
	}
	else if (date[0] == "April") {
		date[0] = "04";
	}
	else if (date[0] == "May") {
		date[0] = "05";
	}
	else if (date[0] == "June") {
		date[0] = "06";
	}
	else if (date[0] == "July") {
		date[0] = "07";
	}
	else if (date[0] == "August") {
		date[0] = "08";
	}
	else if (date[0] == "September") {
		date[0] = "09";
	}
	else if (date[0] == "October") {
		date[0] = "10";
	}
	else if (date[0] == "November") {
		date[0] = "11";
	}
	else {
		date[0] = "12";
	}
	
	date[1] = date[1].slice(0, -1);
	if (date[1].length == 1) {
		date[1] = "0".concat(date[1]);
	}
	date[2] = date[2];
	
	return date[2] + '-' + date[0] + '-' + date[1];
}

function loadDashboardData() {
	/*
	* Requests user data based on the date range and constructs graphs for display.
	* 
	* @return {void} Nothing.
	*/
	var dates = document.getElementById('dates');
	dates = dates.innerText.split("-");
	dates[0] = returnFormattedDate(dates[0]);
	dates[1] = returnFormattedDate(dates[1]);
	
	var xhr = new XMLHttpRequest();
	// 
	xhr.open('GET', '/dashboard-data/' + dates[0] + '/' + dates[1] + '/');
	xhr.onload = function() {
		if (xhr.status === 200) {
			var data = JSON.parse(xhr.responseText);
			
			let last_glucose = document.getElementById('last_glucose');
			let last_carb = document.getElementById('last_carb');
			let last_insulin = document.getElementById('last_insulin');
			
			last_insulin.innerHTML = 'Insulin:<br>&emsp;&emsp;' + data.last_insulin;
			last_glucose.innerHTML = 'Glucose:<br>&emsp;&emsp;' + data.last_glucose;
			last_carb.innerHTML = 'Carb:<br>&emsp;&emsp;' + data.last_carb;
			
			
			let circle_charts = createProgressCircles(data.progress_circles);
			let bar_chart_glucose = createPercentRangeGlucoseBarChart(data.bar_plot_glucose.data);
			let bar_chart_carbs = createPercentRangeCarbsBarChart(data.bar_plot_carbs.data);
			let box_chart = createBoxChart(data.box_plot);
			let insulin_bar_chart = createInsulinBarChart(data.scatter_bar_plot);
			
			Highcharts.chart('max', circle_charts[0]);
			Highcharts.chart('avg', circle_charts[1]);
			Highcharts.chart('min', circle_charts[2]);
			Highcharts.chart('hba1c', circle_charts[3]);
			Highcharts.chart('percent_in_range_glucose', bar_chart_glucose);
			Highcharts.chart('percent_in_range_carbs', bar_chart_carbs);
			Highcharts.chart('box_chart', box_chart);
			Highcharts.chart('insulin_bar_chart', insulin_bar_chart);
		}
		else {
			alert('Request failed.  Returned status of ' + xhr.status);
		}
	};
	xhr.send();
}

function createInsulinBarChart(data) {
	/*
	* Creates a highcharts chart dictionary based on input information.
	*
	* @param {dictionary} data - the scatter/bar plot data containing min/max axis values, plotlines, and the plotted data.
	* 
	* @return {dictionary} the highcarts chart dictionary for the insulin bar chart plot.
	*/
	var plotlines = [];
	for (let index=0; index < data.plotlines.length; index++) {
		plotlines.push({
			color: '#808080', // Red
			width: 1,
			value: data.plotlines[index] // Position, you'll have to translate this to the values on your x axis
		});
	}
	
	bar_chart = {
		credits: {
			enabled: false
		},
		time: {
			useUTC: false
		},
		chart: {
			backgroundColor: '#FCF5F5',
			type: 'scatter',
			zoomType: 'x'
		},
		title: {
			text: 'Insulin Dosage and Carbohydrates over Time',
			style: {
				fontSize: '18px',
				fontFamily: 'Poppins',
				textDecoration: 'Underline',
				color: '#7069AF',
				
			}
		},
		xAxis: [{
			type: 'datetime',
			title: {
				enabled: true,
				text: 'Time',
				style: {
					fontSize: '16px',
					fontFamily: 'Poppins',
					color: '#7069AF',
				}
			},
			min: data.min_time,
			max: data.max_time,
			plotLines: plotlines
		}],
		yAxis: [{
			title: {
				enabled: true,
				text: 'Dosages',
				style: {
					color: Highcharts.getOptions().colors[0]
				}
			},
			min: data.min_dosage,
			max: data.max_dosage
		},
		{
			title: {
				enabled: true,
				text: 'Carbohydrates',
				style: {
					color: 'rgba(223, 83, 83, .5)'
				}
			},
			min: data.min_carbs,
			max: data.max_carbs,
			opposite: true
		}],
		series: [{
			yAxis: 0,
			name: 'Insulin Dosages',
			type: 'column',
			data: data.insulin_data,
			
		},
		{
			yAxis: 1,
			color: 'rgba(223, 83, 83, .5)',
			name: 'Carbohydrate Intake',
			type: 'scatter',
			data: data.carbohydrate_data
		}],
		plotOptions: {
		    scatter: {
				tooltip: {
					headerFormat: '{point.x:%B} {point.x:%e}, {point.x:%Y} at {point.x:%H}:{point.x:%M}:{point.x:%S}<br>',
					pointFormatter: function() {
						var symbol = '';

						switch ( this.series.symbol ) {
							case 'circle':
								symbol = '●';
								break;
							case 'diamond':
								symbol = '♦';
								break;
							case 'square':
								symbol = '■';
								break;
							case 'triangle':
								symbol = '▲';
								break;
							case 'triangle-down':
								symbol = '▼';
								break;
							case undefined:
								symbol = '●';
								break;
						}
						
						return '<span style="color:' + this.series.color + '">' + symbol + '</span>' + '<strong> ' + this.y + '</strong> carbs';
					}
				}
			},
			column: {
				marker: {
					symbol: 'circle'
				},
				tooltip: {
					headerFormat: '{point.x:%B} {point.x:%e}, {point.x:%Y} at {point.x:%H}:{point.x:%M}:{point.x:%S}<br>',
					pointFormatter: function() {
						var symbol = '';

						switch ( this.series.symbol ) {
							case 'circle':
								symbol = '●';
								break;
							case 'diamond':
								symbol = '♦';
								break;
							case 'square':
								symbol = '■';
								break;
							case 'triangle':
								symbol = '▲';
								break;
							case 'triangle-down':
								symbol = '▼';
								break;
							case undefined:
								symbol = '●';
								break;
						}
						
						return '<span style="color:' + this.series.color + '">' + symbol + '</span>' + '<strong> ' + this.y + '</strong> units';
					}
				}
			}
		},
	};
	
	return bar_chart;
}

function createPercentRangeGlucoseBarChart(data) {
	/*
	* Creates a highcharts chart dictionary based on input information.
	*
	* @param {array} data - the data to be graphed.
	* 
	* @return {dictionary} the highcarts chart dictionary for the percent range glucose bar chart plot.
	*/
	bar_chart = {
		credits: {
			enabled: false
		},
		chart: {
			backgroundColor: '#FCF5F5',
			type: 'bar'
		},
		title: {
			text: 'Percentage Glucose in Range',
			style: {
				fontSize: '16px',
				fontFamily: 'Poppins',
				textDecoration: 'Underline',
				color: '#7069AF',
			}
		},
		xAxis: {
			categories: ['Night', 'Morning', 'Afternoon', 'Evening'],
			
		},
		tooltip: {
			formatter: function() {
				return this.series.name.split(" ")[0] + ": " + this.y.toFixed(0) + "%";
			}
		},
		yAxis: {
			min: 0,
			max:100,
			title: {
				text: ''
			},
			labels: {
				enabled: false
			}
		},
		legend: {
			reversed: true
		},
		plotOptions: {
			series: {
				stacking: 'normal'
			}

		},
		series: data
	};
	
	return bar_chart;
}

function createPercentRangeCarbsBarChart(data) {
	/*
	* Creates a highcharts chart dictionary based on input information.
	*
	* @param {array} data - the data to be graphed.
	* 
	* @return {dictionary} the highcarts chart dictionary for the percent range carbs bar chart plot.
	*/
	bar_chart = {
		credits: {
			enabled: false
		},
		chart: {
			backgroundColor: '#FCF5F5',
			type: 'bar'
		},
		title: {
			text: 'Percentage Daily Carbohydrates in Range',
			style: {
				fontSize: '16px',
				fontFamily: 'Poppins',
				textDecoration: 'Underline',
				color: '#7069AF',
			}
		},
		xAxis: {
			categories: ['Day'],
			labels: {
				enabled: false
			}
		},
		tooltip: {
			formatter: function() {
				return this.series.name.split(" ")[0] + ": " + this.y.toFixed(0) + "%";
			}
		},
		yAxis: {
			min: 0,
			max:100,
			title: {
				text: ''
			},
			labels: {
				enabled: false
			}
		},
		legend: {
			reversed: true
		},
		plotOptions: {
			series: {
				stacking: 'normal'
			}

		},
		series: data
	};
	
	return bar_chart;
}

function createBoxChart(data) {
	/*
	* Creates a highcharts chart dictionary based on input information.
	*
	* @param {dictionary} data - the box plot data and outlier data to be graphed.
	* 
	* @return {dictionary} the highcarts chart dictionary for the glucose box plot.
	*/
	box_chart = {
		credits: {
			enabled: false
		},
		exporting: {
			enabled: true
		},
		chart: {
			backgroundColor: '#FCF5F5',
			type: 'boxplot'
		},
		title: {
			text: ''
		},
		legend: {
			enabled: false
		},
		xAxis: {
			categories: ['Night', 'Morning', 'Afternoon', 'Evening'],
			title: {
				text: 'Time',
				style: {
					fontSize: '16px',
					fontFamily: 'Poppins',
					color: '#7069AF',
				}
			}
		},
		yAxis: {
		   title: {
			  text: 'Glucose (mg/dL)',
			  style: {
				fontSize: '16px',
				fontFamily: 'Poppins',
				color: '#7069AF',
			}
		   },
		   min:40,
		   max:400,
		   
		   plotLines: [{
				color: '#FF0000', // Red
				width: 1,
				value: 80 // Position, you'll have to translate this to the values on your x axis
			},
			{
				color: '#FF0000', // Red
				width: 1,
				value: 160 // Position, you'll have to translate this to the values on your x axis
			}]
		},
		series: [{
			name: 'Glucose Values (mg/dL)',
			data: data.data
		},
		{
			name: 'Outliers',
			color: '#7069AF',
			type: 'scatter',
			data: data.outliers,
			marker: {
			fillColor: 'white',
			lineWidth: 1,
			lineColor: Highcharts.getOptions().colors[0]
			},
			tooltip: {
				pointFormat: '{point.y} mg/dL'
			}
		}]
		
	};
	
	return box_chart;
}

function createProgressCircles(data) {
	/*
	* Creates a highcharts chart dictionary based on input information.
	*
	* @param {dictionary} data - min, max, avg, and hba1c values.
	* 
	* @return {dictionary} the highcarts chart dictionary for the progress circles.
	*/
	if (data.min > 160) {
		let max = 400 - 160;
		let min_value = data.min - 160;
		var min_angle = Math.round((1 - min_value / max) * 360);
	}
	else if (data.min < 80) {
		let max = 80 - 40;
		let min_value = data.min - 40;
		var min_angle = Math.round(min_value / max * 360);
	}
	else {
		var min_angle = 360;
	}
	
	min_chart = {
		credits: {
			enabled: false
		},
		exporting: {
			enabled: false
		},
		tooltip: {
			enabled: false
		},
		chart: {
			backgroundColor: '#FCF5F5',
			type: 'solidgauge',
			events: {
				render() {
					let chart = this,
					label1 = chart.series[0].dataLabelsGroup;
					label1.translate(chart.marginRight, chart.marginBottom + label1.getBBox().height*1.2);
				}
			}
		},
		title: {
			text: ''
		},
		pane: {
			startAngle: -90,
			endAngle: min_angle - 90,
			background: [{
				outerRadius: '112%',
				innerRadius: '100%',
				borderWidth: 0
			}]
		  },

		yAxis: {
			min: 0,
			max: 1,
			lineWidth: 0,
			tickPositions: []
		},

		series: [{
			data: [{
				color: '#7069AF',
				radius: '112%',
				innerRadius: '100%',
				y: data.min,
				dataLabels: {
					y: -70,
					format: 'Min Glucose: <br/>{y}',
					borderWidth: 0,
					style: {
						fontSize: '16px',
						fontFamily: 'Poppins',
						textDecoration: 'Underline',
						color: '#7069AF',
					}
				}
			}]
		}],
	};
	
	if (data.avg > 160) {
		let max = (400 - 160) / 2;
		let min_value = data.avg - 160;
		var avg_angle = Math.round((1 - min_value / max) * 360);
	}
	else if (data.avg < 80) {
		let max = 80 - 40;
		let min_value = data.avg - 40;
		var avg_angle = Math.round(min_value / max * 360);
	}
	else {
		var avg_angle = 360;
	}
	
	avg_chart = {
		credits: {
			enabled: false
		},
		exporting: {
			enabled: false
		},
		tooltip: {
			enabled: false
		},
		chart: {
			backgroundColor: '#FCF5F5',
			type: 'solidgauge',
			events: {
				render() {
					let chart = this,
					label1 = chart.series[0].dataLabelsGroup;
					label1.translate(chart.marginRight, chart.marginBottom + label1.getBBox().height*1.2);
				}
			}
		},
		title: {
			text: ''
		},
		pane: {
			startAngle: -90,
			endAngle: avg_angle - 90,
			background: [{
				outerRadius: '112%',
				innerRadius: '100%',
				borderWidth: 0
			}]
		  },

		yAxis: {
			min: 0,
			max: 1,
			lineWidth: 0,
			tickPositions: []
		},

		series: [{
			data: [{
				color: '#7069AF',				
				radius: '112%',
				innerRadius: '100%',
				y: data.avg,
				dataLabels: {
					y: -70,
					format: 'Avg Glucose: <br/>{y}',
					borderWidth: 0,
					style: {
						fontSize: '16px',
						fontFamily: 'Poppins',
						textDecoration: 'Underline',
						color: '#7069AF',
					}
				}
			}]
		}],
	};
	
	if (data.max > 160) {
		let max = 400 - 160;
		let min_value = data.max - 160;
		var max_angle = Math.round((1 - min_value / max) * 360);
	}
	else if (data.max < 80) {
		let max = 80 - 40;
		let min_value = data.max - 40;
		var max_angle = Math.round(min_value / max * 360);
	}
	else {
		var max_angle = 360;
	}
	
	max_chart = {
		credits: {
			enabled: false
		},
		exporting: {
			enabled: false
		},
		tooltip: {
			enabled: false
		},
		chart: {
			backgroundColor: '#FCF5F5',
			type: 'solidgauge',
			events: {
				render() {
					let chart = this,
					label1 = chart.series[0].dataLabelsGroup;
					label1.translate(chart.marginRight, chart.marginBottom + label1.getBBox().height*1.2);
				}
			}
		},
		title: {
			text: ''
		},
		pane: {
			startAngle: -90,
			endAngle: max_angle - 90,
			background: [{
				outerRadius: '112%',
				innerRadius: '100%',
				borderWidth: 0
			}]
		  },

		yAxis: {
			min: 0,
			max: 1,
			lineWidth: 0,
			tickPositions: []
		},

		series: [{
			data: [{
				color: '#7069AF',
				radius: '112%',
				innerRadius: '100%',
				y: data.max,
				dataLabels: {
					y: -70,
					format: 'Max Glucose: <br/>{y}',
					borderWidth: 0,
					style: {
						fontSize: '16px',
						fontFamily: 'Poppins',
						textDecoration: 'Underline',
						color: '#7069AF',
					}
				}
			}]
		}],
	};
	
	let hba1c_average_value = 28.7 * data.hba1c - 46.7;
	
	if (hba1c_average_value > 160) {
		let max = 400 - 160;
		let min_value = hba1c_average_value - 160;
		var hba1c_angle = Math.round((1 - min_value / max) * 360);
	}
	else if (hba1c_average_value < 80) {
		let max = 80 - 40;
		let min_value = hba1c_average_value - 40;
		var hba1c_angle = Math.round(min_value / max * 360);
	}
	else {
		var hba1c_angle = 360;
	}
	
	hba1c_chart = {
		credits: {
			enabled: false
		},
		exporting: {
			enabled: true
		},
		tooltip: {
			enabled: false
		},
		chart: {
			backgroundColor: '#FCF5F5',
			type: 'solidgauge',
			events: {
				render() {
					let chart = this,
					label1 = chart.series[0].dataLabelsGroup;
					label1.translate(chart.marginRight, chart.marginBottom + label1.getBBox().height * 2);
				}
			}
		},
		title: {
			text: ''
		},
		pane: {
			startAngle: -90,
			endAngle: hba1c_angle - 90,
			background: [{
				outerRadius: '112%',
				innerRadius: '100%',
				borderWidth: 0
			}]
		  },

		yAxis: {
			min: 0,
			max: 1,
			lineWidth: 0,
			tickPositions: []
		},

		series: [{
			data: [{
				color: '#7069AF',
				radius: '112%',
				innerRadius: '100%',
				y: data.hba1c,
				dataLabels: {
					y: -70,
					format: "Hba1c: {y}",
					borderWidth: 0,
					style: {
						fontSize: '16px',
						fontFamily: 'Poppins',
						textDecoration: 'Underline',
						color: '#7069AF',
					}
				}
			}]
		}],
	};
	
	return [max_chart, avg_chart, min_chart, hba1c_chart];
}
