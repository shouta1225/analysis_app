from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # リクエストbodyを定義するために必要
from typing import List #ネストされたBodyを定義するために必要
# テキストを返すためのモジュール
# from fastapi.responses import PlainTextResponse
# テキストファイルを返すためのモジュール
from fastapi.responses import FileResponse
# ファイルを返す場合
# from fastapi.responses import StreamingResponse

# 表記ゆれ防止用
import unicodedata
# 正規表現
import re
import sys
import spacy
import csv
import numpy as np

app = FastAPI()

# CORSの設定
origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:8080",
  ]

# リクエストbodyを定義
class TextModel(BaseModel):
  front_text: str

@app.get("/")
def read_root():
    return {"Hello": "World"}
    
# # シンプルなJSON Bodyの受け取り
# @app.post("/api")
# # 上で定義したTextモデルのリクエストbodyをrootのURLで受け取る
# def create_text(text: TextModel):
#   print(text.front_text)
#   return {
#     "status":200,
#     "back_text":text.front_text,
#   }

@app.post("/api")
# 上で定義したTextモデルのリクエストbodyをrootのURLで受け取る
def create_text(text: TextModel):
  # 取得したテキスト
  data_text = text.front_text
  # return{
  #   "text":data_text
  # }
  # urlの正規表現
  url = r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)"

  # stopwordのパス
  stop_word = "./data/Japanese_stopwords.txt"

  '''stopwordの準備'''
  with open(stop_word,'r') as f:
    stop_word = f.read().split('\n')
    # リストで空の要素を削除
    stop_word = list(filter(None, stop_word))

  '''テキスト前処理'''
  # 文字の統一(全ての大文字を小文字に変換)
  lower_text = data_text.lower()
  # 文字の正規化
  normalize_text = unicodedata.normalize("NFKC",lower_text)
  # 文字を0に置換
  normalize_text_none = re.sub(r"[0-9]", "", normalize_text)
  # url除去
  none_url_text = re.sub(url,'',normalize_text_none)
  # print(none_url_text)

  '''形態素解析'''
  # 最終出力する前処理済みのlist
  cleaning_words = []
  # 日本語版のginzaのロード
  nlp = spacy.load('ja_ginza_electra')

  # print(none_url_text)

  # 形態素解析後の単語リスト
  doc = nlp(none_url_text)
  for sent in doc.sents:
    for token in sent:
      '''まずは、品詞詳細で絞ることと、国、地名、人物名を含む分を削る'''
      # 単語が改行、数字を修飾する助数詞可能、括弧だった場合、その処理はスキップ(ただし、数字の場合は別)
      if (token.text == '\n') or (token.tag_ == '名詞-普通名詞-助数詞可能') or (token.tag_ == '補助記号-括弧開') or (token.tag_ == '補助記号-括弧閉') or (token.tag_ == '補助記号-一般') or (token.tag_ == '補助記号一般') or (token.tag_ == '補助記号-句点') or (token.tag_ == '名詞-数詞') or (token.tag_ == '接尾辞-名詞的-一般') or (token.text == ''):
        continue
      # 単語が国や地名の場合は、文章ごと消す
      elif token.tag_ == "名詞-固有名詞-地名-国" or token.tag_ == "名詞-固有名詞-地名-一般" or token.tag_ == '名詞-固有名詞-人名-姓' or token.tag_ == '名詞-固有名詞-人名-名' :
        # print(token.text)
        break
      else:
        if '\n' in token.text:
          token.text.replace('\n','')
        '''次に、stopwordにかける'''
        compare = 0
        for x in range(len(stop_word)):
          if (stop_word[x] == token.lemma_) == True:
            compare += 1
            # print(str(compare) + str(':') + stop_word[x])
          else:
            continue
        # もし、stopwordが1単語に含まれていなかった場合
        if compare == 0:
          # 取得したい文章の単語の中でベクトル化したい単語リスト
          cleaning_words.append([str(token.text) + ',' + str(token.lemma_) + ',' + str(token.pos_)+ ',' + str(token.tag_)+ '\n'])
    # print(cleaning_words)

    # 改行がリスト間に挿入され、結合する
    cleaning_words.insert(0, ["テキスト,レンマ,品詞,品詞詳細\n"])
    print(cleaning_words)

    # ファイル作成
    with open('./data/cleaning_words.csv','w') as g:
      writer = csv.writer(g)
      writer.writerows(cleaning_words)
    
    # フロントエンドにファイルレスポンス
    res = FileResponse(path="./data/cleaning_words.csv")
                      # media_type="text/csv",
                      # filename="cleaning_words.csv")
    
    return res

    # # フロントエンドにcsvファイルのレスポンス
    # res = StreamingResponse(path='./data/cleaning_text.csv',media_type="text/csv",filename="cleaning_text.csv")

    

    # # レスポンスbody
    # # return{"res":"ok", "front_text":text.front_text}
    # # レスポンスcleaning_text
    # # return {"front_text":cleaning_text}
    # # レスポンスtext
    # # return PlainTextResponse(content=cleaning_text)
