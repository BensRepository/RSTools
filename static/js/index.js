

CountDownTimer(['07/18/2023 01:00 AM','07/25/2023 01:00 AM','08/01/2023 01:00 AM',
'08/08/2023 01:00 AM','08/15/2023 01:00 AM','08/22/2023 01:00 AM','08/29/2023 01:00 AM'], 'countdown');

function CountDownTimer(dtList, id)
{
    for (let i = 0; i < dtList.length; i++) {
        var timeItem = new Date(dtList[i]);
        var currentTime = new Date();
        if (timeItem.getTime() > currentTime.getTime()){
            dt = new Date(dtList[i]);
            break
        }
        else{
            continue
        }
       

    }

    var end = new Date(dt);

    var _second = 1000;
    var _minute = _second * 60;
    var _hour = _minute * 60;
    var _day = _hour * 24;
    var timer;

    function showRemaining() {
        var now = new Date();
        var distance = end - now;
        if (distance < 0) {

            clearInterval(timer);
           

            return;
        }
        var days = Math.floor(distance / _day);
        var hours = Math.floor((distance % _day) / _hour);
        var minutes = Math.floor((distance % _hour) / _minute);
        var seconds = Math.floor((distance % _minute) / _second);

        document.getElementById(id).innerHTML = +days + ' Days ';
        document.getElementById(id).innerHTML += hours + ' Hours ';
        document.getElementById(id).innerHTML += minutes + ' Minutes ';
        document.getElementById(id).innerHTML += seconds + ' Seconds';
    }

    timer = setInterval(showRemaining, 1000);
}

