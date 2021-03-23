$a = "%%PAYLOAD%%"
[system.Convert]::toBase64string([System.text.encoding]::Unicode.getbytes($a))
