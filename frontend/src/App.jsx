import React from "react";
import "./App.css"
import { useEffect, useState } from "react";
import axios from 'axios';
import { saveAs } from 'file-saver';


const App = () => {
  // テキストエリアのuseStateを定義
  const [processingTextL, setProcessingTextL] = useState('');
  const [processingTextR, setProcessingTextR] = useState('');

  // ファイル選択エリアのuseStateを定義(初期値は)
  //　とりあえずのフロントエンドなので、未使用
  // const [fileInputText, setFileInputText] = useState();

  const onChangeProcessingTextL = (event) => setProcessingTextL(event.target.value);
  const onChangeProcessingTextR = (event) => setProcessingTextR(event.target.value);

  // checkボタンをクリックした際にテキストエリアまたはファイル選択によるテキストをバックエンドに送るための関数
  const onClickSendText = () => {
    // テキストがふたつ入力されていない場合はクリックするとAlertが返される
    if (processingTextL === '' && processingTextR === ''){
      alert('テキストを入力してください');
    }
    // テキストがふたつ入力されている場合はバックエンドに送信される
    else if (processingTextL !== '' && processingTextR !== ''){
      axios.post('/api', {
        front_text: processingTextL,
        front_text: processingTextR,
        responseType: "Application/json"
      })
        .then((response) => {
          console.log('success');
          console.log(response);
        })
        .catch((error) => {
          console.log(error);
        });
      alert('テキストを送信しました')
    }  
    // checkボタンを押すとテキスト内の値を消す(残った方がいい場合もあるかもだからちょっと考え所)
    setProcessingTextL("");
    setProcessingTextR("");
  };

  // [ToDo] もっと良い書き方があると思うが、とりあえずはこれで
  // 左側のテキストエリアの削除ボタンを押した際にテキストエリアの値を削除する関数
  const onClickDeleteL = () => {
    if (setProcessingTextL !== '') {
      // テキストエリアの値を削除
      setProcessingTextL('');
    }
    else return;
  };
   
  // 右側のテキストエリアの削除ボタンを押した際にテキストエリアの値を削除する関数
  const onClickDeleteR = () => {
    if (setProcessingTextR !== '') {
      // テキストエリアの値を削除
      setProcessingTextR('');
    }
    else return;
  };




  return (
    <>
      <body>
        <header>
          <p id='title'>テキストデータ前処理アプリ</p>
          <nav className="menu">
            <ul id="menu-list">
              <li ><a href="#">Home</a></li>
              <li><a href="#">Commentary</a></li>
              <li><a href="#">Data</a></li>
            </ul>
          </nav>
        </header>
        <div>
          {/* 形態素解析器の選択(本当は2重のプルダウンメニュー) */}
          {/* 形態素解析器を選択すると辞書のプルダウンメニューが取得できるように追加でプルダウンメニューが出てくる */}
          <select name="形態素解析器" id="morphorogical" size="1">
            <option value="形態素解析器" selected hidden>形態素解析器を選択してください</option>
            <option value="Ginza" id="ginza">Ginza:v5.1.2_SudachiPy:v0.6.6</option>
            <option value="Mecab" id="mecab">Mecab</option>
            <option value="Janome++" id="janome++">Janome++</option>
          </select>
        </div>
        <div>
          {/* 辞書の選択 */}
          <select name="辞書" className="dictionaly" size="1">
            <option value="辞書" selected hidden>辞書を選択してください</option>
            <option value="IPA辞書" id="IPA">IPA辞書</option>
            <option value="NEologd" id="NEologd">NEologd</option>
            <option value="Sudachi" id="Sudachi">Sudachi</option>
          </select>
        </div>
        {/* 注意点入力 */}
        <p id="important-point">※文字数50、行数20行まで入ります。それ以上の場合は、サイト左下のファイルを選択で、.txtファイルを選択してください</p>

        {/* <form method="post" action="http://127.0.0.1:8000"> */}
        <form className="fetchform">
          <div className="text-contents">
            {/* テキスト入力 */}
            <textarea name="text" cols="50" rows="20" placeholder="テキストを入力してください" method="post" value={processingTextL} onChange={onChangeProcessingTextL}></textarea>
            <textarea name="text" cols="50" rows="20" placeholder="テキストを入力してください" method="post" value={processingTextR} onChange={onChangeProcessingTextR}></textarea>
          </div>
          <div className="select_click_contents">
            {/* ファイルの選択 */}
            {/* <input type="file" accept=".txt" name="file" id="file" onChange={onFileInputChange} multiple /> */}
            {/* 文章チェック機能 */}
            <input type="button" name="check" value="チェック" id="check" onClick={onClickSendText} />
            {/* テキスト削除、ファイル削除機能 */}
            <input type="button" name="delete" value="削除" id="delete" onClick={onClickDeleteL} />
            <input type="button" name="delete" value="削除" id="delete" onClick={onClickDeleteR} />
            {/* 解説ページへの遷移ボタン */}
            <input type="button" name="commentary" value="解説" id="commentary" />
          </div>
        </form>

        <div className="create-data">
          {/* ここに解析(前処理)結果を出力する */}
          <a href="csv_url">cleaning_words.csv</a>
        </div>

        <footer>
          <div className="wrapper">
            <p><small>&copy; 2023 processing app</small></p>
          </div>
        </footer>
      </body>
    </>
  );
}

export default App;

