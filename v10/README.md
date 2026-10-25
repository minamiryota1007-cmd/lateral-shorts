# ラテラルシンキング Ver.10 — 30秒版

既存のv9を残し、v10に6シーン30秒（1080x1920、30fps、900フレーム）の動画生成プログラムを実装。

## 実行方法
WindowsのVOICEVOXを起動。Node.js、Python3.13、Python requests/imageio-ffmpeg を使用。

PowerShellで次を順番に実行:

```powershell
$zip = "$env:TEMP\lateral-v10.zip"
$folder = "$env:USERPROFILE\lateral-v10"
Invoke-WebRequest "https://github.com/minamiryota1007-cmd/lateral-shorts/archive/refs/heads/main.zip" -OutFile $zip
Expand-Archive -Path $zip -DestinationPath $folder -Force
Set-Location "$folder\lateral-shorts-main\v10"
$env:PIXABAY_API_KEY = Read-Host "Pixabay API Key"
powershell -ExecutionPolicy Bypass -File .\run_windows.ps1
```

生成先: `v10/out/magnum_v10.mp4`。生成成功後自動再生。

VOICEVOXは男性「青山龍星」。Pixabayの素材が見つからない場合、Remotionの図形・背景に切り替える。銃の実写映像や空の実写感は取得できる映像素材に左右される。ユーザー保有の権利処理済み映像は `v10/public/assets/revolver.mp4`、`sky.mp4` などに配置可能。ランタイムでの最終MP4検証は未実施。

説明はCd=0.45の単純化したケースのみに統一。弾丸10.2g、秒速330m、エネルギー約555J、球4.72kg・高さ12m相当、完全鉛直・無風で最高約888m、頂点約10.54秒の条件付き試算。**正確な実銃の飛翔高度を保証する数字ではない**。弾丸の回転や姿勢までは静止しない。

888m地点で人が実際に捕まえる描写は行わず、危険性のある捕獲が不可能であることを明示。安全なCG/VFX表現のみ。

公開時はVOICEVOX音声ライセンスに従い「VOICEVOX:青山龍星」など必要なクレジットを記載。
