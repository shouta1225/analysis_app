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
            # separation_words.append(token.text) # 単語だけのリストを作って、後にそれぞれの単語をカウントする
      # print(cleaning_words)
  # 改行がリスト間に挿入され、結合する
  cleaning_words.insert(0, ["テキスト,レンマ,品詞,品詞詳細'\n'"])
  # cleaning_text = '\n'.join(cleaning_words)
  # print('-------' + mode + '-------')
  print(cleaning_words)

# 一度テキストのみを入れるリストを作る→数を数える→もし、形態素結果が必要ならテキストのみリストと形態素結果の中で一致するものを取得する
  rank_words = []
  count = collections.Counter(cleaning_words)
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

@app.post("/api/bunsetu_top100")
'''
テキストデータから文節解析と形態素解析を行い、そのセットをjson形式で返す
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
# 表作成
import pandas as pd
# jsonを扱う
import json
import glob
from pprint import pprint
# sqlite3を扱う
import sqlite3

# 日本語版のginzaのロード
nlp = spacy.load('ja_ginza_electra')

''' ファイルをフロントエンドから取得してくる'''
paths = glob.glob('./sample/cyber_agent.txt')
# paths = glob.glob('./sample/mixi.txt')
# text = 'これは例です。\n実際は、複数のファイルが必要です。'

# 案としてあらかじめ10社データをDBに登録しておく？ただそれだと柔軟性に欠ける
# テキストファイルを1社ずつ出力(今回は1社のみだが、実際は、フロントエンドから取得した複数社)

'''品詞詳細がこのリストの中にあれば削除できる形にする'''
delete_flag = ['助動詞','助詞-格助詞','助詞-係助詞','助詞-準体助詞',
            '助詞-終助詞','補助記号-読点','助詞-接続助詞','動詞-非自立可能',
            '補助記号-句点','接尾辞-名詞的-助数詞','接尾辞-名詞的-副詞可能','接頭辞',
            '補助記号-括弧開','補助記号-括弧閉','接続詞','補助記号-一般',
            '名詞-数詞','名詞-普通名詞-助数詞可能','接尾辞-名詞的-一般','副詞',
            '名詞-普通名詞-副詞可能','連体詞','形状詞-助動詞語幹']

# 全データが入るclausesを定義
clauses = {}
clauses_list = []

'''最終的にtop100を出力するための新しいjson形式'''
new_clauses = {}
new_clause_list = []

for path in paths:
    # print(path)
    # 企業名の辞書を設定するため
    company_name = path.replace('./sample/','')
    company_name = company_name.replace('.txt','')
    print(path)
    with open(path,'r') as f:
        # ginzaの一度での解析容量を考え文章をsplit(タブ、改行、スペースで区切る)
        text = f.read().split()

    '''一番上位にくる文節ごとの全ての区分(中身:word(文節)、mor(形態素)、count(文節の出現個数))'''
    all_list = {}
    # key:企業名,value:['BUNSETU_LIST']:[],"文節"
    company_dic = {}
    '''最終的にcompany_dicに変わる場所'''
    new_company_dic = {}
    # 頻度が高い文節トップ100を降順で入れたもの
    BUNSETU_LIST = []
    # 文節が初めて登場した時に入れる重複なしの文節リスト
    bunsetu_list = []

    bunsetu_dic = {}
    '''最終的にbunsetu_dicに変わる場所'''
    new_bunsetu_dic = {}
    # 全ての文節を追加
    bunsetu_all_list = []
    # 文節を出現回数のランキングの降順に100個入れる
    # rank_bunsetu = []
    num = 0

    # textから1行ずつ取得
    for line in text:
        doc = nlp(line)
        # 引数に与えられたdocに含まれる文節区間を依存関係ラベルと共に返す。
        for bunsetu in ginza.bunsetu_spans(doc):
            mor_dic = {}
            # 文節の中の形態素のリスト
            mor_list = []
            # dep['count'] = 0
            # bunsetu[str(bunsetu)] = {}
            '''全文節を追加(bunsetuのカウントに使う)'''
            bunsetu_all_list.append(str(bunsetu))

            if str(bunsetu) in bunsetu_list:
                continue
            else:# 文節がリストに含まれてない場合、リストに追加
                bunsetu_list.append(str(bunsetu))
                # num += 1
                
                '''文節から形態素解析を行い、リストに追加'''
                for token in bunsetu:
                    # 文節の中の形態素のリストの中の辞書("word","delete_flag")
                    word_and_delete_dic = {}
                    delete_judge = False # 付属語かどうかの初期値
                    if token.tag_ in delete_flag:# OK
                        delete_judge = True
                    word_and_delete_dic['word'] = token.text + ',' + token.lemma_+',' + token.pos_ + ',' + token.tag_ # 文節の中の形態素の一つ
                    word_and_delete_dic['delete_flag'] = delete_judge
                    # print(word_and_delete_dic)
                    mor_list.append(word_and_delete_dic)
                mor_dic["mor"] = mor_list
                mor_dic["count"] = 1 # 文節カウントの初期値
                # key:文節にvaluse:morを入れる
                bunsetu_dic[str(bunsetu)] = mor_dic
    # key:企業名に入れる企業を指定してそのvalueに文節を代入する
    company_dic[company_name] = bunsetu_dic


    bunsetu_and_num = []
    rank_bunsetu = []
    # # 文節の数をカウントする
    count = collections.Counter(bunsetu_all_list)
    # print(count.most_common(100))
    '''文節の出現数から多い方の100個からタプル型を出してそれをリスト型に直して二重リストに追加'''
    for word_and_num in count.most_common(100):
        rank_bunsetu.append(list(word_and_num)) # 二重リストの[文節,回数]
        BUNSETU_LIST.append(word_and_num[0])
    # print(rank_bunsetu) #ok
    # print(BUNSETU_LIST) ok
    '''top文節100とjson上の文節が一致した場合、その文節のカウントを入れ替える'''
    for j in range(len(rank_bunsetu)):
        # print(rank_bunsetu[j][0]) # ok
        for json_bunsetu in bunsetu_all_list:
            if rank_bunsetu[j][0] == json_bunsetu:
                # カウントの回数を変更
                company_dic[company_name][rank_bunsetu[j][0]]['count'] = rank_bunsetu[j][1]
                # print(clauses_list[0][company_name][rank_bunsetu[j][0]]['count'])
                # d = OrderedDict.fromkeys(clauses_list[0][company_name][json_bunsetu])
                # 結果をnew_bunsetu_dicに入れる
                # ※文節の順番がずれる
                new_bunsetu_dic[rank_bunsetu[j][0]] = company_dic[company_name][rank_bunsetu[j][0]]
                # pprint.pprint(sorted(new_bunsetu_dic[rank_bunsetu[j][0]], key=lambda x: x['count'], reverse=True))
    # pprint(new_bunsetu_dic)
    new_bunsetu_dic['BUNSETU_LIST'] = BUNSETU_LIST
    new_company_dic[company_name] = new_bunsetu_dic
    # pprint(new_company_dic)
    # new_clauses_list.append(new_company_dic)
    # new_clauses['clauses'] = clauses_list

    # pprint(new_clauses)

# jsonファイル出力
json_path = path.replace('./sample','./db_json')
json_path = json_path.replace('.txt','.json')
# print(json_path)
writing_json = json.dumps(new_company_dic, indent=2, ensure_ascii=False)
# print(writing_json)
with open(json_path,'w') as g:
    g.write(writing_json)

# dbname = 'main.db'
# # DBを作成する
# conn = sqlite3.connect(dbname)
# db = sqlite3.connect