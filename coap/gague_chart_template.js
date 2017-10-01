      google.charts.load('current', {'packages':['gauge']});
      google.charts.setOnLoadCallback(drawChart);

      function drawChart() {

        var data_solar = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Solar', 350]
        ]);
        
        var data_photo = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Photosynthetic', 30]
        ]);
        
        var data_motor = google.visualization.arrayToDataTable([
          ['Label', 'Value'],
          ['Motor', 0]
        ]);
        
       
        var options_solar = {
          width: 500, height: 150,
          redFrom: 4000, redTo: 5000,
          yellowFrom:3500, yellowTo: 4000,
          greenFrom:300, greenTo:3500,
          minorTicks: 5, max: 5000,
          greenColor:'#99FF33',
          yellowColor:'#FFE333'
        };
        
        var options_photo = {
          width: 500, height: 150,
          redFrom: 400, redTo: 500,
          yellowFrom:350, yellowTo: 400,
          greenFrom:30, greenTo:350,
          minorTicks: 5, max: 500,
          greenColor:'#99FF33',
          yellowColor:'#FFE333'
        };
        
        var options_motor = {
          width: 500, height: 150,
          redFrom: 0.5, redTo: 1,
          greenFrom:0, greenTo:1,
          minorTicks: 0.5, max: 1,
          greenColor:'#99FF33'
        };
        
        

        var chart_solar = new google.visualization.Gauge(document.getElementById('chart_div_solar'));
        var chart_photo = new google.visualization.Gauge(document.getElementById('chart_div_photo'));
        var chart_motor = new google.visualization.Gauge(document.getElementById('chart_div_motor'));

        chart_solar.draw(data_solar, options_solar);
        chart_photo.draw(data_photo, options_photo);
        chart_motor.draw(data_motor, options_motor);
        
        setInterval(function() {
          data_solar.setValue(0, 1, 300 + Math.round(30 * Math.random()));
          chart_solar.draw(data_solar, options_solar);
        }, 1000);
        setInterval(function() {
          data_photo.setValue(0, 1, 30 + Math.round(3 * Math.random()));
          chart_photo.draw(data_photo, options_photo);
        }, 1000);
        setInterval(function() {
          data_motor.setValue(0, 1, 0 + Math.round(1 * Math.random()));
          chart_motor.draw(data_motor, options_motor);
        }, 1000);

      }