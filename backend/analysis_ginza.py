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
    
    return res

@app.post("/api/files")
def test_code():
  print('success')
  return 'success'
'''
1.一つのファイルまたはテキストから取得した文章をGiNZA(オプションA単語,B単語,C単語)を用いて形態素解析&Cleaningを行う。
2.その単語集をtoken.textを基準にカウントする
3.その結果を、上位順に表を作って表す。
A,B,C単語でGiNZA形態素解析
'''

# 表記ゆれ防止用
import unicodedata
# 正規表現
import re
import sys
import spacy
import ginza
# 文字数をそれぞれカウントする
import collections
# 文字列から指定したindexの要素を取得するためのモジュール
from operator import itemgetter

# 文字列が半角の英数字もので構成されたものかどうかを判定する関数
def isalnum_ascii(s):  # 文字列のメソッドを使用
  if s.isalnum() or s.isascii():
    return True
  else:
    return False

text = "これはお試しの形態素解析用のものです。お試しの割には、企業もめんどくさいことやらないといけない。KKKKK読み込みと読込と読込み。\nhttps://shouta.jpもう大学にきたくないし、研究もしたくない。\njwaoghwoghwoghwoghweghiowevhioewghewoghewofghewofghewiofhewioghewoghewghewogvhewoghi\n疲れた\noighrwoghwoghw"
shape_text = []

# urlの正規表現
url = r"(https?|ftp)(:\/\/[-_\.!~*\'()a-zA-Z0-9;\/?:\@&=\+\$,%#]+)"

# stopwordのパス
stop_word = "data/Japanese_stopwords.txt"

'''stopwordの準備'''
with open(stop_word,'r') as f:
  stop_word = f.read().split('\n')
  # リストで空の要素を削除
  stop_word = list(filter(None, stop_word))

'''テキスト前処理'''
# 文字の統一(全ての大文字を小文字に変換)
text = text.lower()
# 文字の正規化
text = unicodedata.normalize("NFKC",text)
# url除去
text = re.sub(url,'',text)
# print(text)
text = text.split('\n')
# print(text)

# 20文字より多い英語だけで構成されている文と20文字より少ない文は削除
for line in text:
  if (len(line) > 20 and isalnum_ascii(line) == False) and (len(line) > 20):
    shape_text.append(line)
# print(shape_text)

'''形態素解析'''
# 最終出力する前処理済みのlist
# cleaning_words = []
# 日本語版のginzaのロード
nlp = spacy.load('ja_ginza_electra')

for mode in ['A', 'B', 'C']:
  cleaning_words = []
  separation_words = []
  print('-'*5, '動作モード:', mode, '(デフォルト)' if mode=='C' else '')
  ginza.set_split_mode(nlp, mode)# モード切替

  for shape_line in shape_text:
    doc = nlp(shape_line)
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
            cleaning_words.append([str(token.text) + ',' + str(token.lemma_) + ',' + str(token.pos_)+ ',' + str(token.tag_) + '\n'])
            # 分かち書きした単語のみを取得
            separation_words.append(token.text) # 単語だけのリストを作って、後にそれぞれの単語をカウントする
      # print(cleaning_words)
  # 改行がリスト間に挿入され、結合する
  cleaning_words.insert(0, ["テキスト,レンマ,品詞,品詞詳細'\n'"])
  # cleaning_text = '\n'.join(cleaning_words)
  # print('-------' + mode + '-------')
  print(cleaning_words)

# 一度テキストのみを入れるリストを作る→数を数える→もし、形態素結果が必要ならテキストのみリストと形態素結果の中で一致するものを取得する
  rank_words = []
  count = collections.Counter(separation_words)
  for k,v in sorted(count.items(), key=itemgetter(1), reverse=True):
    rank_words.append(k + ',' + str(v))
    # print("%s = %d個" %(k, v))
  print(rank_words)
    

      # return{
      #   "text":cleaning_text
      # }

      # ファイル作成
      # with open('./data/cleaning_text.csv','w') as g:
      #   g.write(cleaning_text)

      # フロントエンドにファイルレスポンス
      # res = FileResponse(path="./data/cleaning_text.csv",
      #                   media_type="text/plain")

      # フロントエンドにcsvファイルのレスポンス
      # res = StreamingResponse(path='./data/cleaning_text.csv')

      # レスポンスbody
      # return{"res":"ok", "front_text":text.front_text}
      # レスポンスcleaning_text
      # return {"front_text":cleaning_text}
      # レスポンスtext
      # return PlainTextResponse(content=cleaning_text)
