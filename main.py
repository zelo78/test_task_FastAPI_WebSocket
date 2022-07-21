from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/")
async def root():
    script = r"""
            const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/add_thing/');
            
            const sleepLogInput = document.querySelector('#sleep-log-input')
            const sleepLog = document.querySelector('#sleep-log')
            const sleepLogSubmit = document.querySelector('#sleep-log-submit')

            chatSocket.onmessage = function(e) {
                const data = JSON.parse(e.data);
                sleepLog.innerHTML += ('#' + data.number + ' ' + data.thing + '<br>');
            };

            chatSocket.onclose = function(e) {
                console.error('Chat socket closed unexpectedly');
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
            };
            
            sleepLogInput.onkeyup = function(e) {
                if (e.keyCode === 13) { // enter, return
                    sendMessage();
                }
            };

            sleepLogSubmit.onclick = sendMessage;
    """

    content = f"""
    <!DOCTYPE html>
        <html lang="ru">
            <head>
                <title>Sleep log</title>
            </head>
            <body>
                <h1>Ваш сон</h1>
                <h2>Всё, что Вы увидели в этом сне</h2>
                <text-area readonly id="sleep-log">
                </text-area>
                <hr>
                <p>Вводите то, что Вы видите во сне, по одной мысли за раз, и нажимайте кнопку "Я увидел!"</p>  
                <input id="sleep-log-input" type="text" size="100"><br>
                <input id="sleep-log-submit" type="button" value="Я увидел!">
                
                <script>
                {script}
                </script>
            </body>
        </html>
        """
    response = HTMLResponse(content=content)
    return response


@app.websocket("/ws/add_thing/")
async def websocket_endpoint(
    websocket: WebSocket,
):
    number = 0
    await websocket.accept()
    while True:
        try:
            # Wait for any message from the client
            data = await websocket.receive_json()
            thing = data.get("thing")
            number += 1
            await websocket.send_json({"thing": thing, "number": number})
        except Exception as e:
            print("error:", e)
            break
    print("Bye..")
