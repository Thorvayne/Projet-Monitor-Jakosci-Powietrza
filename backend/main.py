from fastapi import FastAPI

app = FastAPI(title="Air Quality API")

@app.get("/")
def read_root():
    return {"message": "Backend działa! Czeka na kod Krzyśka."}
