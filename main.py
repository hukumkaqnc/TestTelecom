from fastapi import FastAPI, Depends, Body
from sqlalchemy import func
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, ForeignKey, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from initdb import *
from random import randint

Base.metadata.create_all(bind=engine)
app = FastAPI()
#db = SessionLocal()
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()



@app.get("/")
def main():
    return FileResponse("public/index.html")

# @app.get("/test")
# def test(db: Session = Depends(get_db)):
#     res = db.query(Tariff.id).filter(Tariff.name == 'Турбо').all()
#     print(res[0][0])
#     return {'res':'ok'}

@app.get("/get/tarrifs")
def get_tarrifs(db: Session = Depends(get_db)):
    t = db.query(Tariff).all()
    return t
@app.get("/get/contracts")
def get_contracts(db: Session = Depends(get_db)):
    c = db.query(Contracts).all()
    return c
@app.get("/get/contr/{id}")
def get_contract(id, db: Session = Depends(get_db)):
    
    contr = db.query(Contracts).filter(Contracts.id == id).first()
    
    if contr==None:  
        return JSONResponse(status_code=404, content={ "message": "contr не найден"})
    
    return contr
@app.get("/get/addr/{id}")
def get_address(id, db: Session = Depends(get_db)):
    
    addr = db.query(Address).filter(Address.id == id).first()
    
    if addr==None:  
        return JSONResponse(status_code=404, content={ "message": "addr не найден"})
    print(addr)
    return addr
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
@app.get("/get/balance/{id}")
def get_balance(id, db: Session = Depends(get_db)):
    b = db.query(func.sum(Incoming.value)).filter(Incoming.cont_id == id).group_by(Incoming.cont_id).first()
    
    print(b)
    if b == None:
        return {'value': 0}
    return {'value': b[0]}

@app.post("/tariff/{na}/{pri}")
def create_tarif(na: str, pri: int, db: Session = Depends(get_db)):
    
    tar = Tariff(name = na, price = pri)
    db.add(tar)
    db.commit()
    return tar

@app.post("/add/inc")
def incoming(data  = Body(), db: Session = Depends(get_db)):
    inc = Incoming(value = data['value'], date = data['date'], cont_id = data['cont_id'] )
    db.add(inc)
    db.commit()
    return inc

@app.delete("/delete/contr/{id}")
def delete_person(id, db: Session = Depends(get_db)):
    
    contr = db.query(Contracts).filter(Contracts.id == id).first()
 
    if contr == None:
        return JSONResponse( status_code=404, content={ "message": "Пользователь не найден"})
   
    db.delete(contr)  
    db.commit()  
    return contr

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)