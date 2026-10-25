# Lateral Shorts V3 — Windows

The original scripts remain unchanged. V3 creates a narrated vertical Shorts MP4 in Windows using Python, VOICEVOX and FFmpeg (bundled with imageio-ffmpeg).

## First run

1. Start VOICEVOX and verify http://127.0.0.1:50021/version responds.
2. Python 3.13 (64-bit), Pillow, requests, numpy, opencv-python and imageio-ffmpeg are required.
3. Open PowerShell and run:

```powershell
$u = "https://raw.githubusercontent.com/minamiryota1007-cmd/lateral-shorts/main/windows_shorts_v3.py"
$f = "$env:USERPROFILEwindows_shorts_v3.py"
Invoke-WebRequest $u -OutFile $f
& "$env:LOCALAPPDATAProgramsPythonPython313python.exe" $f
```

Output: `C:Users<username>lateral_shorts_v3.mp4`.

## Real moving footage

Optional local clips (recommended, no API required): place portrait MP4 files in:

- `%USERPROFILE%Videoslateral_shorts_assetsstore*.mp4`
- `%USERPROFILE%Videoslateral_shorts_assetswallet*.mp4`
- `%USERPROFILE%Videoslateral_shorts_assetscalendar*.mp4`
- `%USERPROFILE%Videoslateral_shorts_assetsmoney*.mp4`
- `%USERPROFILE%Videoslateral_shorts_assets	ravel*.mp4`

The clip will loop when shorter than the scene.

Optional Pexels Videos API (requires a free key and is subject to their API limits, asset license and attribution requirements):

`$env:PEXELS_API_KEY = "your-own-key"`

V3 downloads footage for missing categories. Do not add keys to GitHub.
If no video is available, V3 uses animated photo backgrounds from Unsplash; if unavailable, animated gradients. V3 DOES NOT generate real AI video. Review terms of any asset before publication.

## Notes

- 30 FPS, upscaled to 1080x1920 H.264 MP4, 6 voice-led scenes.
- Target 30 sec if natural narration fits, otherwise slightly longer; **no forced fast speaking**.
- On-screen calculations use an explicit assumption: ¥600 per pack and 365 days/year.
- Example credits: VOICEVOX:春日部つむぎ. Follow voice character's usage terms.
- Edit `SCENES` in `windows_shorts_v3.py` to change the theme.
- V3 does not automatically generate a new Fermi estimate from free text; that is a later integration.
- Video generation is local, not run by GitHub; runtime depends on PC performance. First-run install/download is not included.
