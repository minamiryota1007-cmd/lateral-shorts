# iPhoneで動画を作る方法

1. GitHubのこのリポジトリで **Actions** を開く
2. **Generate VOICEVOX short** を選ぶ
3. **Run workflow** → **Run workflow** を押す
4. 実行が緑のチェックになったら実行履歴を開く
5. 下の **Artifacts** にある `lateral-short-preview` をダウンロード
6. ZIPを展開し、MP4を再生して確認してからYouTubeへ手動投稿

## 台本の変更
`scripts/script.json` をGitHub上で編集し、`segments` の `text` を書き換えてコミットしてから再実行してください。
字幕と読み上げは同じテキストを使います。数値・推定条件は公開前に検証してください。

## 構成と料金
GitHub ActionsのUbuntuランナーでVOICEVOX EngineのCPU版をDocker起動し、PillowとFFmpegで720×1280の縦型MP4を生成します。APIキーは不要です。GitHub Actionsの無料利用枠・利用規約の範囲内で運用してください。公開リポジトリの標準GitHubホストランナーは通常無料ですが、利用条件は変更されることがあります。

## 注意
- VOICEVOXの音声利用時は使用キャラクターごとの利用規約に従い、動画の概要欄等に適切なクレジットを記載してください（例：VOICEVOX:ずんだもん）。利用規約は公開前に確認してください。
- 自動投稿は実装していません。必ず動画を確認してから投稿してください。
- 音楽・外部映像は含まれません。音声・字幕・背景のみの初期版です。
- 動画生成はまだ実行確認前です。Actionsのログを確認して不具合を修正してください。
