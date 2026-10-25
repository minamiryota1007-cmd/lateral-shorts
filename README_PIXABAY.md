# Pixabay integration (Windows V3)

Pixabay video search is now integrated in `windows_shorts_v3.py`.

## Set your key locally

Never put API keys in a GitHub repository, public issue, or chat message. If previously shared, rotate/regenerate the key from the provider where possible, then use the new one.

PowerShell (current session only):

```powershell
$env:PIXABAY_API_KEY = Read-Host "Pixabay API Key"
$url = "https://raw.githubusercontent.com/minamiryota1007-cmd/lateral-shorts/main/windows_shorts_v3.py"
$file = "$env:USERPROFILE\windows_shorts_v3.py"
Invoke-WebRequest -Uri $url -OutFile $file
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" $file
```

Start VOICEVOX before running. Output: `%USERPROFILE%\lateral_shorts_v3.mp4`.

## Asset selection order

1. Local manually provided MP4 (e.g. `Videos\lateral_shorts_assets\money\*.mp4`)
2. Previously downloaded per-scene video
3. Pixabay Videos API (if PIXABAY_API_KEY present)
4. Pexels video API (if PEXELS_API_KEY present)
5. Animated photograph
6. Animated gradient

Pixabay search metadata is cached for at least 24 hours; downloaded clips are cached locally and reused. It does not indiscriminately bulk-download the whole library. Follow Pixabay API requirements, Content License, and individual asset restrictions. Review footage before publication. Pixabay may return landscape clips which this version resizes; this can distort proportions and will be improved in a future update.

The API key is never embedded in the Python script. `Read-Host` is unmasked in Windows PowerShell: ensure nobody is looking at your screen while typing, or use `Read-Host -AsSecureString` and convert locally if needed.
