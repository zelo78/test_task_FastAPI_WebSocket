from fastapi import Depends, FastAPI, WebSocket, Cookie, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static/templates")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, db: Session = Depends(get_db)):
    # new sleep begins
    sleep = models.Sleep()
    db.add(sleep)
    db.commit()
    db.refresh(sleep)

    response = templates.TemplateResponse(
        name="main.html",
        context={"request": request, "sleep_id": sleep.id},
    )
    response.set_cookie(key="sleep_id", value=str(sleep.id))
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
