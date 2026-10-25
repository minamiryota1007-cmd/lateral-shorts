# ラテラルシンキング Ver.9 — 次元のマグナム弾は素手でキャッチできる？

45秒、9:16、1080×1920、30fps、Remotion + VOICEVOX + Python + Pixabay (任意)。

## 主な改修
1. 7章すべて別の背景素材を優先。Pixabay APIによる自動検索＋ローカル素材キャッシュ。素材がなくても計算・VFXのアニメーションが動作。
2. **555Jの比喩：質量約4.7kgのボウリング球を高さ12mに持ち上げた位置エネルギー。** 衝突時の衝撃そのものが同じとは主張しない。落下の実写撮影は禁止。
3. Python RK4積分で上昇モデルを毎回計算し、\`src/physics.json\`に保存。上昇高度・鉛直速度の数値グラフィックを表示時間と連動。Cd感度分析をバーに反映。
4. VOICEVOXの明るい男性ナレーション（青山龍星、利用可能なら高テンションのスタイル）。音声を途中で切らず、尺に入らない場合は停止して台本短縮を促す。
5. 自作音楽パルスを追加。頂点付近はBGMを一瞬停止。ユーザーが最終MP4を確認してから手動投稿。

## 必要なもの
- Windows 11、PowerShell 5.1
- Node.js/npm ( \`node --version\` と \`npm.cmd --version\` )
- Python 3.13 (\`%LOCALAPPDATA%\Programs\Python\Python313\python.exe\`)
- Python packages: \`requests\`, \`imageio-ffmpeg\`
- VOICEVOX起動中 (http://127.0.0.1:50021)
- (任意) 有効な Pixabay API key を環境変数 \`PIXABAY_API_KEY\` に設定
- VOICEVOX character terms and license must be respected: description credit \`VOICEVOX:青山龍星\`

## 実行
PowerShellで \`v9\` に移動してから：

\`\`\`powershell
powershell -ExecutionPolicy Bypass -File .\run_windows.ps1
\`\`\`

成功したら \`v9\out\magnum_v9.mp4\` を生成して自動再生。

Windows PowerShellが \`npm.ps1\` をブロックしても、スクリプトは \`npm.cmd\` / \`npx.cmd\` を使用する。

## 手動で高品質な映画風映像を使う方法
ライセンス許諾済みの縦動画を \`v9\public\assets\` に次の名前で保存すると、Pixabay APIを使わず優先的に使用:
- \`revolver.mp4\`
- \`bullet.mp4\`
- \`bowling.mp4\`
- \`sky.mp4\`
- \`altitude.mp4\`
- \`range.mp4\`
- \`ending.mp4\`

各素材は9:16、約5〜9秒、無音推奨。素材がなければプログラム生成背景にフォールバックする。

## 数値と限界
- 弾丸質量10.2g / 初速330m/s / 直径9.07mm
- 位置エネルギー比較: \`555.39 / (9.81 × 12) = 約4.72kg\`
- Cd=0.45、空気密度の高度減少を仮定した簡略モデル: 最高高度約888m、頂点約10.54秒
- Cd=0.30〜1.00の感度分析で高さが概ね496〜1,171m
- 風、弾体の姿勢変化、回転に伴う抗力の変化、実際の環境や弾薬の変動を再現していない。**実射の弾道予測や安全な捕獲方法の説明ではない。**
- 最高点で0になるのは*鉛直速度成分*のみ。現実の横風や回転は残り得る。
- 屋外で発射したり落下させたりする実験は絶対に行わないこと。

## 現在の完成度
GitHubに動作を想定したコードを保存済み。ユーザーのWindowsでのレンダリング実行は未検証。Runway無料プランでは動画生成を使えないため、映画並みのCG素材そのものを自動AI生成するわけではない。高いリアリティを得るには、事前に権利処理済みの実写・VFX素材を配置する必要がある。参考動画との完全な一致は保証しない。
