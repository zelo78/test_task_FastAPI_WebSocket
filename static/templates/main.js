const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/add_thing/');
const sleepLogInput = document.querySelector('#sleep-log-input');
const sleepLog = document.querySelector('#sleep-log');
const sleepLogSubmit = document.querySelector('#sleep-log-submit');

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    sleepLog.innerHTML += ('#' + data.number + ' ' + data.thing + '<br>');
};

chatSocket.onclose = function(e) {
    window.console.error('Chat socket closed unexpectedly');
};

sleepLogInput.focus();

function sendMessage(e) {
    const message = sleepLogInput.value;
    if (message !== '') {
        chatSocket.send(
            JSON.stringify({'thing': message})
        );
    }
    sleepLogInput.value = '';
}

sleepLogInput.onkeyup = function(e) {
    if (e.keyCode === 13) { // enter, return
        sendMessage();
    }
};

sleepLogSubmit.onclick = sendMessage;