from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:8080",
  ]

# リクエストbodyを定義
class TextModel(BaseModel):
  front_textL: str
  front_textR: str

@app.post("/api")
def rec_text_res_json(text: TextModel):
    print(text.front_textL)
    print(text.front_textR)
    # ディレクトリ内にある、jsonファイルをフロントエンドへ返す
    with open('cyber_agent.json', 'r') as f:
        data = json.load(f)
    return {
        "status":200,
        "back_text":data,
        "type":"Application/json"
    }