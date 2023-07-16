from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
import json


class Prices(models.Model):
    id = fields.IntField(pk=True)
    date = fields.DateField()
    cargo_type = fields.CharField(max_length=50)
    rate = fields.FloatField()


    @classmethod
    def get_json(cls):
        dct = {
            cls.date: {
            "cargo_type": cls.cargo_type,
            "rate": cls.rate
            }
        }
        return json.dumps(dct)


Prices_Pydantic = pydantic_model_creator(Prices, name="Prices")
PricesIn_Pydantic = pydantic_model_creator(Prices, name="PricesIn", exclude_readonly=True)

