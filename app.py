from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from acb import ACB


app = FastAPI()

class LoginDetails(BaseModel):
    username: str
    password: str
    account_number: str
@app.post('/login', tags=["login"])
def login_api(input: LoginDetails):
        acb = ACB(input.username, input.password, input.account_number)
        result = acb.login()
        return result

@app.post('/get_balance', tags=["get_balance"])
def get_balance_api(input: LoginDetails):
        acb = ACB(input.username, input.password, input.account_number)
        result = acb.login()
        balance = acb.get_balance()
        return balance
class Transactions(BaseModel):
    username: str
    password: str
    account_number: str
    rows: int
    
@app.post('/get_transactions', tags=["get_transactions"])
def get_transactions_api(input: Transactions):
        acb = ACB(input.username, input.password, input.account_number)
        result = acb.login()
        history = acb.get_transactions(input.account_number, input.rows)
        return history
if __name__ == "__main__":
    uvicorn.run(app ,host='0.0.0.0', port=3000)