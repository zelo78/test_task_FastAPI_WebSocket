from fastapi import Depends, FastAPI, HTTPException, WebSocket, Cookie
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root(db: Session = Depends(get_db)):
    db_sleep = models.Sleep()
    db.add(db_sleep)
    db.commit()
    db.refresh(db_sleep)
    sleep_id = db_sleep.id

    script = r"""
            const chatSocket = new WebSocket('ws://' + window.location.host + '/ws/add_thing/');

            chatSocket.onmessage = function(e) {
                const data = JSON.parse(e.data);
                /* document.querySelector('#chat-log').value += (data.message + '\n'); */
                /* document.querySelector('#chat-log').innerHTML += (data.message + '<br>'); */
                document.querySelector('#sleep-log').innerHTML += ('#' + data.number + ' ' + data.thing + '<br>');
                for (const i in data.results) {
                    document.querySelector('#sleep-log').innerHTML +=
                    '<a href="' + data.results[i][1] + '">' +
                    data.results[i][0] + '</a><br>';
                }
                /* document.querySelector('#chat-log').rows += 1; */
            };

            chatSocket.onclose = function(e) {
                console.error('Chat socket closed unexpectedly');
            };

            document.querySelector('#sleep-log-input').focus();

            document.querySelector('#sleep-log-input').onkeyup = function(e) {
                if (e.keyCode === 13) { // enter, return
                    document.querySelector('#sleep-log-submit').click();
                }
            };

            document.querySelector('#sleep-log-submit').onclick = function(e) {
                const messageInputDom = document.querySelector('#sleep-log-input');
                const message = messageInputDom.value;
                if (message !== '') {
                    chatSocket.send(JSON.stringify({
                        'thing': message
                    }));
                }
                messageInputDom.value = '';
            };
    """

    content = f"""
    <!DOCTYPE html>
        <html lang="ru">
            <head>
                <title>Sleep log</title>
            </head>
            <body>
                <h1>Сон номер {sleep_id}</h1>
                <h2>Всё, что Вы увидели в этом сне</h2>
                <text-area readonly id="sleep-log">
                </text-area>
                <hr>
                <p>Вводите то, что Вы видите во сне, по одной мысли за раз, и нажимайте кнопку "Я увидел!"</p>  
                <form>
                    <input id="sleep-log-input" type="text" size="100"><br>
                    <input id="sleep-log-submit" type="button" value="Я увидел!">
                </form>
                
                <script>
                {script}
                </script>
            </body>
        </html>
        """
    response = HTMLResponse(content=content)
    response.set_cookie(key="sleep_id", value=str(sleep_id))
    return response


@app.websocket("/ws/add_thing/")
async def websocket_endpoint(
    websocket: WebSocket,
    sleep_id: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    number = 0
    await websocket.accept()
    while True:
        try:
            # Wait for any message from the client
            data = await websocket.receive_json()
            thing = data.get("thing")
            number += 1

            db_thing = models.Thing(number=number, name=thing, owner_id=sleep_id)
            db.add(db_thing)
            db.commit()
            db.refresh(db_thing)

            await websocket.send_json({"thing": thing, "number": number})
        except Exception as e:
            print("error:", e)
            break
    print("Bye..")


@app.get("/sleeps/", response_model=list[schemas.Sleep])
async def get_sleeps(db: Session = Depends(get_db)):
    return db.query(models.Sleep).all()


@app.get("/things/", response_model=list[schemas.Thing])
async def get_sleeps(db: Session = Depends(get_db)):
    return db.query(models.Thing).all()
