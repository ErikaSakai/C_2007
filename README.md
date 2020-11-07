# ポーチマン 〜一家に一台を見据えたロボット活用置き配支援サービス〜

[![IMAGE ALT TEXT HERE](https://jphacks.com/wp-content/uploads/2020/09/JPHACKS2020_ogp.jpg)](https://www.youtube.com/watch?v=G5rULR53uMk)

## 製品概要
### 背景(製品開発のきっかけ、課題等）
通販の受取方法として再配達の防止のため，「置き配」という手段が用いられている．．
また，昨今のコロナウイルスの蔓延により，配達業者との接触を行わずに配達物が受け取れることが利点でもある「置き配」が主流となってきているが，コロナの影響を受け，盗難の問題が顕著になってきた．従来手法として自宅玄関と紐で繋がれた袋に配達物をいれるシステムなどが存在しているが，盗難の保証はされているものの，盗難の防止は不十分である．そこで，私たちnUCLeusはsociety5.0の推進化に伴い，ロボットの普及が見込まれることを想定し，ロボットを活用することによりこの問題に取り組む．

### 製品説明（具体的な製品の説明）
今回はPepperに内蔵されたカメラと顔認証機能に着目し，Pepperが配達物の受取を行うこと家庭内における荷物の代替受取システムを実現する．
ユーザはあらかじめPepperに到着予定の荷物の配達番号を送信しておく．Pepperは自身の前に人が立ったことを検知すると，その人物を撮影してユーザに写真を送信する．配達業者はPepper前面のタブレットに配達番号を入力する．Pepperはその入力が事前にユーザが登録した情報と等しいことを確認することで配達を認識する．配達が行われた時，Pepperはユーザに配達完了通知を送信する．
Pepperには事前にユーザの顔の判別器を作成しておく．これにより，配達物がある状態でPepperの前にユーザが現れた時，配達物を受け取ることができる．

### 特長
* カメラや人感センサを搭載したロボットが配達物を受け取ることで，セキュリティ面が強化される
* 人型ロボットが配達業者にお礼や労いを直接伝えることが可能なため，配達業者も笑顔に
* LINEと連携したサービスであるため，ユーザの導入難易度が低い

### 解決出来ること
* ユーザ不在のため発生する再配達問題
* 置き配手法における盗難問題

### 今後の展望
配達業者が訪問した際に，インターホンの音などをトリガーとし，玄関のドアと連携することで，Pepperが家から外に出て配達物を受け取り，宅内へ帰っていくようにすることが可能であると考えている．
### 注力したこと（こだわり等）
* 
* 

## 開発技術
### 活用した技術
#### API・データ
* LINE Messaging API
* Microsoft Azure App Service
* Microsoft Azure storage account

#### フレームワーク・ライブラリ・モジュール
* Choregraphe
* Python
* Azure for a python
* Flask

#### デバイス
* Pepper
* Raspberry Pi 3 model B
* Smart Phpne


#### サービス説明動画
* https://youtu.be/A3rBV8bqIa0
* 
