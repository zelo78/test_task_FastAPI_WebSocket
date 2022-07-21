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
                <h1>Сон номер {sleep_id}</h1>
                <h2>Всё, что Вы увидели в этом сне</h2>
                <text-area readonly id="sleep-log">
                </text-area>
                <hr>
                <p>Вводите то, что Вы видите во сне, по одной мысли за раз, и нажимайте кнопку "Я увидел!"</p>  
                <form action='#'>
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
