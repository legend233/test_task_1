from collections import defaultdict
from fastapi import FastAPI, HTTPException
from models import Prices_Pydantic, Prices
from schemas import Prices_load, Status
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise


app = FastAPI()


@app.get("/prices", response_model=Prices_load)
async def get_prices():
    """Get all prices from database"""
    lst = await Prices_Pydantic.from_queryset(Prices.all())
    dct = defaultdict(list)
    for item in lst:
        item = item.dict()
        dct[item["date"].strftime('%Y-%m-%d')].append({"cargo_type": item["cargo_type"], "rate": item["rate"]})
    return dict(dct)


@app.post("/prices")
async def create_prices(prices: Prices_load):
    """Add new prices in format:
    {"2020-07-01":[{"cargo_type":"Glass","rate":0.04},{"cargo_type":"Other","rate":0.015}]}
    """
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
    """Get actual price"""
    get_obg_list = await Prices_Pydantic.from_queryset(Prices.filter(date__lt=get_date, cargo_type=cargo_type).order_by('-date'))
    if get_obg_list:
        result = get_obg_list[0]
        return {result.date: {"cargo_type": result.cargo_type, "rate": result.rate}}
    else:
        return {"message": "Not found"}


@app.delete("/price/{get_date}/{cargo_type}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_price(get_date: str, cargo_type: str):
    """Delete price from database"""
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
