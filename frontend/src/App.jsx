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
    if (processingTextL === '' || processingTextR === '') {
      alert('テキストを入力してください');
    }
    // テキストがふたつ入力されている場合はバックエンドに送信される
    else if (processingTextL !== '' && processingTextR !== '') {
      axios.post('/api', {
        front_textL: processingTextL,
        front_textR: processingTextR,
        responseType: "Application/json"
      })
        .then((response) => {
          var data = response.data.back_text;
          console.log(data);
          var list = document.getElementById('word_list');
          for (var key in data) {
            var details = document.createElement('details');
            var summary = document.createElement('summary');
            summary.innerHTML = key+' '+ data[key].count;
            var table = document.createElement('table');
            var tr = document.createElement('tr');
            var th1 = document.createElement('th');
            var th2 = document.createElement('th');
            var th3 = document.createElement('th');
            var th4 = document.createElement('th');
            th1.innerHTML = '単語';
            th2.innerHTML = 'レンマ';
            th3.innerHTML = '品詞';
            th4.innerHTML = '品詞細分類';
            tr.appendChild(th1);
            tr.appendChild(th2);
            tr.appendChild(th3);
            tr.appendChild(th4);
            table.appendChild(tr);
            for (var i = 0; i < data[key].mor.length; i++) {
              var tr = document.createElement('tr');
              var td1 = document.createElement('td');
              var td2 = document.createElement('td');
              var td3 = document.createElement('td');
              var td4 = document.createElement('td');
              td1.innerHTML = data[key].mor[i].split(',')[0];
              td2.innerHTML = data[key].mor[i].split(',')[1];
              td3.innerHTML = data[key].mor[i].split(',')[2];
              td4.innerHTML = data[key].mor[i].split(',')[3];
              tr.appendChild(td1);
              tr.appendChild(td2);
              tr.appendChild(td3);
              tr.appendChild(td4);
              table.appendChild(tr);
            }
            details.appendChild(summary);
            details.appendChild(table);
            list.appendChild(details);
          }
        })
        .catch((error) => {
          console.log(error);
        });
      alert('テキストを送信しました')
    }
    // checkボタンを押すとテキスト内の値を消す(残った方がいい場合もあるかもだからちょっと考え所)
    // setProcessingTextL("");
    // setProcessingTextR("");
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

  const onClickCommentary = () => {
    // ページスクロール
    // [ToDo] innerHeightを使ってスクロールするようにしたい
    window.scrollTo(0, 1000);
  };
 
  return (
    <>
      <body>
        <div className='phase1'>
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
              <input type="button" name="commentary" value="解説" id="commentary" onClick={onClickCommentary} />
            </div>
          </form>
        </div>
        <div className='phase2'>
          <div className='word_list' id='word_list'></div>
        </div>
      </body>
    </>
  );
}

export default App;
