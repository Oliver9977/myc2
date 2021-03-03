function Get-CompressedByteArray {

	[CmdletBinding()]
    Param (
	[Parameter(Mandatory,ValueFromPipeline,ValueFromPipelineByPropertyName)]
        [byte[]] $byteArray = $(Throw("-byteArray is required"))
    )
	Process {
        Write-Verbose "Get-CompressedByteArray"
       	[System.IO.MemoryStream] $output = New-Object System.IO.MemoryStream
        $gzipStream = New-Object System.IO.Compression.GzipStream $output, ([IO.Compression.CompressionMode]::Compress)
      	$gzipStream.Write( $byteArray, 0, $byteArray.Length )
        $gzipStream.Close()
        $output.Close()
        $tmp = $output.ToArray()
        Write-Output $tmp
    }
}

$filename = "payload\myclient.exe"
$old_bytes = [IO.File]::ReadAllBytes($filename)
$new_bytes = Get-CompressedByteArray -byteArray $old_bytes
[system.Convert]::toBase64string($new_bytes) | Clip
[system.Convert]::toBase64string($new_bytes)

