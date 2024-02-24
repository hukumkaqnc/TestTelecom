from fastapi import FastAPI, Depends, Body
from sqlalchemy import func
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, ForeignKey, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from initdb import *
from random import randint

#модуль реализующий связь бд и фронта, в котором исполняются 
#get, post, put, delete запросы к бд


Base.metadata.create_all(bind=engine)
app = FastAPI() #запуск сервера

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()
#настройка обращений к сессии orm


@app.get("/")
def main():
    return FileResponse("public/index.html")
#открытие начальной страницы интерфейса, запрос возвращает html документ


@app.get("/get/tarrifs")
def get_tarrifs(db: Session = Depends(get_db)):
    t = db.query(Tariff).all()
    return t
#возвращает список тарифов
@app.get("/get/contracts")
def get_contracts(db: Session = Depends(get_db)):
    c = db.query(Contracts).all()
    return c
#возвращает список договоров
@app.get("/get/contr/{id}")
def get_contract(id, db: Session = Depends(get_db)):
    
    contr = db.query(Contracts).filter(Contracts.id == id).first()
    
    if contr==None:  
        return JSONResponse(status_code=404, content={ "message": "contr не найден"})
    
    return contr
#возвращает конкретный договор либо сообщение об ошибке если такой не найден
@app.get("/get/addr/{id}")
def get_address(id, db: Session = Depends(get_db)):
    
    addr = db.query(Address).filter(Address.id == id).first()
    
    if addr==None:  
        return JSONResponse(status_code=404, content={ "message": "addr не найден"})
    print(addr)
    return addr
#возвращает конкретный адрес по id метод используется для редактирования договора
@app.post("/add/contract")
def create_contract(data  = Body(), db: Session = Depends(get_db)):
    ad = db.query(Address.id).filter(Address.city == data['city'], 
    Address.srteet == data['street'], 
    Address.build == data["build"],
    Address.apart == data['apart']).all()
    if(ad == []):
        new_addr = Address(city = data['city'],
        srteet = data['street'],
        build = data["build"],
        apart = data['apart'])
        db.add(new_addr)
        db.commit()
        
        ad = db.query(Address.id).filter(Address.city == data['city'], 
        Address.srteet == data['street'], 
        Address.build == data["build"],
        Address.apart == data['apart']).all()
    print(ad)
    s = 'abcdefghigklmnopqrstuvwzyx-1234567890'
    id = ""
    for i in range(12):
        id += s[randint(0, len(s)-1)]
    id+='h'
    contract = Contracts(id = id, 
    fio=data["fio"], 
    is_phys = data["is_phys"], 
    status = data["status"], 
    addr = ad[0][0], 
    tariff = int(data["tariff"]))
    db.add(contract)
    db.commit()
    
    return contract
# функция создает новый договор, ключ для договора генерируется автоматически, функция проверяет существует ли адрес указанный в форме
# и если его нет, создает новый адрес.
# примечание для генерации номера договора в идеале должен использоваться слеш, но так как номер договора является первичным ключем 
# и фигурирует в запросах, данный символ мешает нормальной работе сервера. Не знаю насколько данный вопрос принципиален, переделывать уже не стал, 
# так как проблема всплыла при отладке, и пришлось бы переделать бд, но в случае если это принципиально могу переделать
@app.put("/edit/contract")
def edit_contr(data  = Body(), db: Session = Depends(get_db)):
   
    print('point')
    contr = db.query(Contracts).filter(Contracts.id == data["id"]).first()
    print(contr)
    if contr == None: 
        return JSONResponse(status_code=404, content={ "message": "Пользователь не найден"})
    
    contr.fio=data["fio"], 
    
    contr.status = data["status"], 
    
    contr.tariff = int(data["tariff"])
    db.commit() 
    
    return contr
# функция для редактирования пользователя
@app.get("/get/balance/{id}")
def get_balance(id, db: Session = Depends(get_db)):
    b = db.query(func.sum(Incoming.value)).filter(Incoming.cont_id == id).group_by(Incoming.cont_id).first()
    
    print(b)
    if b == None:
        return {'value': 0}
    return {'value': b[0]}
# функция для получения баланса пользователя
@app.post("/tariff/{na}/{pri}")
def create_tarif(na: str, pri: int, db: Session = Depends(get_db)):
    
    tar = Tariff(name = na, price = pri)
    db.add(tar)
    db.commit()
    return tar
# создание нового тарифа, не работает с интерфейсом напрямую, чтоб добавить тариф, функцию нужно вызывать  из /docs
@app.post("/add/inc")
def incoming(data  = Body(), db: Session = Depends(get_db)):
    inc = Incoming(value = data['value'], date = data['date'], cont_id = data['cont_id'] )
    db.add(inc)
    db.commit()
    return inc
#функция для фиксаций пополлнений баланса
@app.delete("/delete/contr/{id}")
def delete_person(id, db: Session = Depends(get_db)):
    
    contr = db.query(Contracts).filter(Contracts.id == id).first()
 
    if contr == None:
        return JSONResponse( status_code=404, content={ "message": "Пользователь не найден"})
   
    db.delete(contr)  
    db.commit()  
    return contr
#функция для удаления договора, так как к каждому договору привязаны платежи, для удаления договора был также написан триггер на pl/pgsql
# был реализован в pgAdmin, код триггера прилагается в проекте

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)