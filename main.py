from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []

items = {
    "foo": {"name": "Foo", "price": 50.2, "tax": 10.5, "tags": []},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2, "tags": []},
}

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    return items[item_id]

@app.patch("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    stored_data = items[item_id]
    stored_model = Item(**stored_data)
    update_data = item.dict(exclude_unset=True)
    updated = stored_model.copy(update=update_data)
    items[item_id] = jsonable_encoder(updated)
    return updated


