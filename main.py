from enum import Enum
from fastapi import FastAPI

app = FastAPI()

# Define an enum
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name == ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning pioneer!"}
    if model_name == ModelName.resnet:
        return {"model_name": model_name, "message": "Residual connections FTW!"}
    return {"model_name": model_name, "message": "LeNet – old but gold"}
