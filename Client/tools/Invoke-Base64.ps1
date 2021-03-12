$filename = "payload\myclient.exe"
$old_bytes = [IO.File]::ReadAllBytes($filename)
[system.Convert]::toBase64string($old_bytes) | Clip
[system.Convert]::toBase64string($old_bytes)

