# Modified to include support for CommandLine, File Hashes, File Paths, Signing Certificates
# Copyright (c) 2020 Jai Minton. All rights reserved.
# Copyright (c) 2014 Atif Aziz. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Adapted from http://p0w3rsh3ll.wordpress.com/2012/10/12/show-processtree/


function Get-ProcessTree
{
    [CmdletBinding()]
    param([string]$ComputerName, [int]$IndentSize = 2)
    
    $indentSize   = [Math]::Max(1, [Math]::Min(12, $indentSize))
    $computerName = ($computerName, ".")[[String]::IsNullOrEmpty($computerName)]
    $processes    = Get-WmiObject Win32_Process -ComputerName $computerName
    $pids         = $processes | select -ExpandProperty ProcessId
    $parents      = $processes | select -ExpandProperty ParentProcessId -Unique
    $liveParents  = $parents | ? { $pids -contains $_ }
    $deadParents  = Compare-Object -ReferenceObject $parents -DifferenceObject $liveParents `
                  | select -ExpandProperty InputObject
    $processByParent = $processes | Group-Object -AsHashTable ParentProcessId
    
    function Write-ProcessTree($process, [int]$level = 0)
    {
        $id = $process.ProcessId
        $processCommandLine = $process.CommandLine
		$parentProcessId = $process.ParentProcessId
        $user = $process.getowner().user
        $process = Get-Process -Id $id -ComputerName $computerName
		$hash	= ($process | gi -ea SilentlyContinue|filehash -ea 0).hash
		$signingstatus	= ($process | gi -ea SilentlyContinue|authenticodesignature -ea 0).status
        $indent = New-Object String(' ', ($level * $indentSize))
        $process `
        | Add-Member NoteProperty CommandLine $processCommandLine -PassThru `
		| Add-Member NoteProperty ParentId $parentProcessId -PassThru `
        | Add-Member NoteProperty Level $level -PassThru `
		| Add-Member NoteProperty Hash $hash -PassThru `
		| Add-Member NoteProperty signature $signingstatus -PassThru `
        | Add-Member NoteProperty IndentedName "$indent$($process.Name)" -PassThru `
        | Add-Member NoteProperty Owner $user -PassThru
        $processByParent.Item($id) `
        | ? { $_ } `
        | % { Write-ProcessTree $_ ($level + 1) }
    }

    $processes `
    | ? { $_.ProcessId -ne 0 -and ($_.ProcessId -eq $_.ParentProcessId -or $deadParents -contains $_.ParentProcessId) } `
    | % { Write-ProcessTree $_ }
}

<# Usage: 
import-module .\Get-ProcessTree.ps1

Get-ProcessTree -Verbose | select Id, Level, IndentedName, ParentId

OR for more verbose output:

Get-ProcessTree -Verbose | FT Id, Level, IndentedName,ParentId,Path,Hash,CommandLine -AutoSize
Get-ProcessTree -Verbose | FT Id, Level, IndentedName,ParentId,Hash,CommandLine -AutoSize
Get-ProcessTree -Verbose | FT Id, Level, IndentedName,ParentId,Hash,signature,CommandLine -AutoSize
Get-ProcessTree -Verbose | FT Id, Level, IndentedName,ParentId,Path,CommandLine,Owner -AutoSize
#>