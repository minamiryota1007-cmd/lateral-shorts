# 皇帝ペンギン３号：動くショート

GitHub Actionsの「Penguin motion short」を選び、Run workflowを押すと、VOICEVOXのナレーションとBGM付きMP4を作成します。完了した実行のArtifactsにある `penguin-motion-preview` をダウンロードしてください。YouTubeには自動投稿しません。

映像はイラストを場面ごとに切り替え、カメラの移動・拡大で動きを付けたものです。ペンギンの手足や表情が独立して動く動画生成AIではありません。場面絵は `assets/0.jpg`〜`6.jpg` を置き換えると変更できます。

推定は氷の上を時速10kmで、ボールを運びながら一定速度で進む仮定です。公式設定・実測値ではありません。

Windowsで実行する場合、FFmpegとPythonを用意しVOICEVOXを起動してから `python penguin_motion/render.py` を実行します。ナレーション不要の確認用は `python penguin_motion/render.py --no-voice`。ボイスIDの既定は13、変更するには `--speaker 8` のように指定してください。音声は各場面に収まらない場合、途中で切らずエラーで停止します。
