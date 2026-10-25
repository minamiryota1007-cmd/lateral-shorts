# ラテラルシンキング V7 (Remotion)

既存のV6までを壊さず、`v7/` 以下に追加した新しい動画制作エンジンです。

## 機能

- 1080×1920、30 fps、46秒（合計1380フレーム）
- 同じ色調に統一した都市・信号機背景のアニメーション（Remotion + SVG/CSS）。**Blenderによる本格3Dは未実装**
- 20の信号、41%ゲージ、60秒時計、式の計算アニメーション、カレンダー、約55日間のバー
- Windows上のVOICEVOX APIから青山龍星の音声をシーンに沿って合成
- MP4自動出力と再生
- 検査レポートは作成しない

## 前提

- Windows 11
- Node.js LTS と npm（PowerShellで `node --version` と `npm --version`）
- Python 3.13（既定の場所 `%LOCALAPPDATA%\Programs\Python\Python313\python.exe`）、`requests` インストール済み
- VOICEVOX起動中（http://127.0.0.1:50021）＋青山龍星キャラクターの音声
- 初回の `npm install` にはインターネット接続が必要

## 実行

1. GitHubの `main` ブランチをZIPでダウンロードして展開する（既にgitが使える場合はgit cloneでも可）
2. フォルダ `lateral-shorts-main\v7` に移動
3. PowerShellで `powershell -ExecutionPolicy Bypass -File .\run_windows.ps1` を実行

実行が完了したら `v7\out\lateral_v7.mp4` が作成され、既定の動画プレーヤーで開きます。

## コマンドによる確認

PowerShellで `npm run studio` を実行すると映像のプレビュー・編集ができます。VOICEVOXなしで試したいときは `npm install` の後 `npm run render` （**音声なし**）。

## 内容の計算

全て**仮定**です。1日20か所、赤で止まる割合41%、1回60秒 → 1日492秒＝8.2分。年間240日、40年 → 78,720分＝約54.67日。

この割合は交通統計の公表値を示すものではありません。通勤ルート・信号制御・実際の待ち時間により大きく異なります。

## 公開時の注意

VOICEVOXの利用規約に従い、動画説明欄などで適切に `VOICEVOX:青山龍星` とクレジットしてください。先に台本・数値・背景の適切さを自分で確認してください。Remotionの利用規約・ライセンスも利用形態に応じて確認してください。

## 未実装

- Blenderで作成した3D背景との合成
- 題材を自然言語で入力し自動台本生成
- Pixabay動画素材の自動取得をV7へ統合（V6には残っています）
- 参考動画の完全再現（同一の3Dアセット・シネマティックCGではありません）

まずは再生できるV7デモとして実装し、背景素材とテーマ生成を後で強化する構成です。
