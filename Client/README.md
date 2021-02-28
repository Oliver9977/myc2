# To Generate Powershell-Invoke Version 

- Use `Invoke-Compression` from `Bypass\powershell-Invoke\C#loader\`
- Change `$filename` to the path of C# binary
- Get the result of `[system.Convert]::toBase64string($new_bytes)`
- Copy the result to tempelte `Invoke-myclient.ps1` and replace b64 string in `$a`
