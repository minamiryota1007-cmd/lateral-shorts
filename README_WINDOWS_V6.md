# Windows Shorts V6

This is a new version; earlier versions are preserved.

## Windows PowerShell

Start VOICEVOX first. Ensure the **current PowerShell session** has `PIXABAY_API_KEY` set; if not, set it privately with `$env:PIXABAY_API_KEY = Read-Host "Pixabay API Key"`. Never paste API keys into GitHub.

```powershell
$url = "https://raw.githubusercontent.com/minamiryota1007-cmd/lateral-shorts/main/windows_shorts_v6.py"
$file = "$env:USERPROFILE\windows_shorts_v6.py"
Invoke-WebRequest -Uri $url -OutFile $file
& "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" $file
if ($LASTEXITCODE -eq 0) { Start-Process "$env:USERPROFILE\lateral_shorts_v6.mp4" }
```

Output: `%USERPROFILE%\lateral_shorts_v6.mp4`.

Features: cinematic real footage (Pixabay if obtainable), frame-by-frame count-up totals, 5-step progress bar, animated clock and money bars, on-screen numerals, separate voice text for correct pronunciation of `1箱` as `ひとはこ`, low male VOICEVOX 青山龍星, tax and lifetime cigarette cost narrative.

All estimates are based on explicit assumptions (600 JPY/pack, 1 pack/day, 365 days/year, 50 years, 5 min/cigarette). Taxes are part of the stated retail spend, **not additional spending**; tobacco tax rates, packs and consumption tax may vary by date/product. Footage searches are opportunistic; the pipeline falls back to moving photos and does not fully re-create the sample video's custom CGI. Original video has not been rendered or visually checked on the user's PC.
