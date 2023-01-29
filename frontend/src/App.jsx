import React from "react";
import "./App.css"
import { useEffect, useState } from "react";
import axios from 'axios';
import { saveAs } from 'file-saver';


const App = () => {
  // useState定義
  // テキストエリアのuseStateを定義
  const [processingText, setProcessingText] = useState('');

  // ファイル選択エリアのuseStateを定義(初期値は)
  const [fileInputText, setFileInputText] = useState();

  // FastAPIから返ってきたcsvファイルを保存するためのuseState
  // const [responseCSV, setResponseCSV] = useState();

  /* 関数の定義 */
  // 入力した値(processingText)をuseStateを使って変更するための関数
  const onChangeProcessingText = (event) => setProcessingText(event.target.value);

  // ファイルの選択(e.target.files→ファイル名他ファイルの情報が入っている)
  const onFileInputChange = (event) => {
    // ファイル選択がキャンセルされた場合はundefined
    const fileInputText = event.target.files[0];
    setFileInputText(() => {
      return fileInputText ? fileInputText : undefined;
    });
  }

  // const onFileInputChange = (e) => {
  //   let selectedFile = e.target.files
  //   console.log(e.target.files)
  // }
  // http://backend:8000


  // checkボタンをクリックした際にテキストエリアまたはファイル選択によるテキストをバックエンドに送るための関数
  const onClickSendText = () => {
    // alert(processingText)
    // alert(fileInputText)

    // テキスト、ファイル共に持っていない場合はクリックするとalertが返される
    if (processingText === '' && fileInputText === undefined) alert('ファイルの選択、またはテキストを入力してください');

    // ファイルを持っていないが、テキストを持っている場合
    else if (fileInputText === undefined && processingText !== '') {
      axios.post('/api', {
        front_text: processingText,
        responseType: "blob"
      })
        .then((response) => {
          const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' });
          saveAs(blob, 'response.csv');
          console.log(response);
          console.log(blob);
        })
        .catch((error) => {
          console.log(error);
        });
      alert('テキストを送信しました')
    }
    // テキストを持っていないが、ファイルを持っている場合
    else if (processingText === '' && fileInputText !== undefined) {
      // 複数のファイルを /apiFiles にPOSTする
      const formData = new FormData();
      formData.append('file', fileInputText);
      axios.post('/api/files', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
        .then((response) => {
          // 複数のcsvファイルを保存する
          const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8;' });
          saveAs(blob, 'response.csv');
          console.log(response);
          console.log(blob);
        })
        .catch((error) => {
          console.log(error);
        });
      alert('ファイルを送信しました')
    }
    else if (processingText !== '' && fileInputText !== undefined) {
      console.log(processingText)
      console.log(fileInputText)
      alert('ファイルかテキストのどちらかだけを選択してください。');
    }
    // 全てに当てはまらない場合は、エラーアラートを返す
    else {
      alert('error')
    }

    // checkボタンを押すとテキスト内の値を消す(残った方がいい場合もあるかもだからちょっと考え所)
    setProcessingText("");
  };


  // 削除ボタンを押した時、テキストエリアまたはファイル選択の削除を行う
  const onClickDelete = () => {
    if (setProcessingText !== '') {
      // テキストエリアの値を削除
      setProcessingText('');
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
            <textarea name="text" cols="50" rows="20" placeholder="テキストを入力してください" method="post" value={processingText} onChange={onChangeProcessingText}></textarea>
          </div>
          <div className="select_click_contents">
            {/* ファイルの選択 */}
            <input type="file" accept=".txt" name="file" id="file" onChange={onFileInputChange} multiple />
            {/* 文章チェック機能 */}
            <input type="button" name="check" value="チェック" id="check" onClick={onClickSendText} />
            {/* テキスト削除、ファイル削除機能 */}
            <input type="button" name="delete" value="削除" id="delete" onClick={onClickDelete} />
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

