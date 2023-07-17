import json
from collections import defaultdict
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from models import Prices_Pydantic, PricesIn_Pydantic, Prices
from pydantic import BaseModel

from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise


app = FastAPI()


test_data = '''{"2020-07-01":[{"cargo_type":"Glass","rate":0.04},{"cargo_type":"Other","rate":0.015}],"2020-06-01":[{"cargo_type":"Glass","rate":0.035},{"cargo_type":"Other","rate":0.01}]}'''

class Rate_valid(BaseModel):
    cargo_type: str
    rate: float

class Prices_load(BaseModel):
    __root__: Dict[str, List[Rate_valid]]

class Status(BaseModel):
    message: str


@app.get("/prices", response_model=Prices_load)
async def get_prices():
    lst = await Prices_Pydantic.from_queryset(Prices.all())
    dct = defaultdict(list)
    for item in lst:
        item = item.dict()
        dct[item["date"].strftime('%Y-%m-%d')].append({"cargo_type": item["cargo_type"], "rate": item["rate"]})
    return dict(dct)


@app.post("/prices")
async def create_prices(prices: Prices_load):
    main_dct = prices.dict()['__root__']
    lst = []
    for key in main_dct.keys():
        dct = dict()
        for item in main_dct[key]:
            dct['date'] = key
            dct["cargo_type"] = item["cargo_type"]
            dct["rate"] = item["rate"]
            await Prices.create(**dct)
            lst.append(dct.copy())
            dct.clear()
    return lst


@app.get(
    "/price/{get_date}/{cargo_type}", responses={404: {"model": HTTPNotFoundError}}
)
async def get_price(get_date: str, cargo_type: str):
    get_obg = await Prices_Pydantic.from_queryset_single(Prices.get(date=get_date, cargo_type=cargo_type))
    return {get_obg.date: {"cargo_type": get_obg.cargo_type, "rate": get_obg.rate}}
# TODO make right get_price

@app.delete("/price/{get_date}/{cargo_type}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_price(get_date: str, cargo_type: str):
    deleted_count = await Prices.filter(date=get_date, cargo_type=cargo_type).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"Price at date {get_date} and cargo type {cargo_type} not found")
    return Status(message=f"Price is Deleted")


register_tortoise(
    app,
    db_url="sqlite://db/sqlite.db",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
