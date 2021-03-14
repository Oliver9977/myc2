function Get-32BitProcess {
<#
.SYNOPSIS
Gets 32-bit processes running on the local 64-bit Windows computer.

.DESCRIPTION
By default, all accessible 32-bit processes are returned:

- Without elevation, you're limited to querying processes created in the context
  of the current user, and a warning to that effect is displayed.

- With elevation, all system-wide 32-bit processes are output; inaccessible
  system process (which are inherently 64-bit) are ignored.
  To see which ones are ignored, pass -Verbose.

This function is in effect a filtering wrapper around Get-Process that only
operates on 32-bit processes.

Parameters are the same as for Get-Process, with the following exceptions:

* only *local* 32-bit processes can be retrieved, so the -ComputerName parameter 
  is not supported.

* parameters -FileVersionInfo and -Module are not supported; however, you 
  can simply pipe this function's output to a Get-Process call with these
  parameters.

Note that you'll only get output for a given process if it is indeed a 32-bit
process; when in doubt, pass -Verbose.

.NOTES
Inspired by https://stackoverflow.com/a/23025963/45375

Refuses to run on 32-bit editions of Windows, because the distinction between
32-bit and 64-bit is only meaningful in 64-bit editions.

.LINK
Get-Process

.EXAMPLE
> Get-32BitProcess
With elevation: outputs all 32-bit processes.
Without elevation: outputs the current user's 32-bit processes.

.EXAMPLE
> Get-32BitProcess -ID $PID
Implicitly tests if the current process is 32-bit: if it is, information about
the process is output; if not, there's no ouptut.
#>
  [CmdletBinding(DefaultParameterSetName='Name')]
  param(
    [Parameter(ParameterSetName='NameWithUserName', Position=0, ValueFromPipelineByPropertyName=$true)]
    [Parameter(ParameterSetName='Name', Position=0, ValueFromPipelineByPropertyName=$true)]
    [Alias('ProcessName')]
    [ValidateNotNullOrEmpty()]
    [string[]]
    ${Name},

    [Parameter(ParameterSetName='Id', Mandatory=$true, ValueFromPipelineByPropertyName=$true)]
    [Parameter(ParameterSetName='IdWithUserName', Mandatory=$true, ValueFromPipelineByPropertyName=$true)]
    [Alias('PID')]
    [int[]]
    ${Id},

    [Parameter(ParameterSetName='InputObject', Mandatory=$true, ValueFromPipeline=$true)]
    [Parameter(ParameterSetName='InputObjectWithUserName', Mandatory=$true, ValueFromPipeline=$true)]
    [System.Diagnostics.Process[]]
    ${InputObject},

    [Parameter(ParameterSetName='IdWithUserName', Mandatory=$true)]
    [Parameter(ParameterSetName='NameWithUserName', Mandatory=$true)]
    [Parameter(ParameterSetName='InputObjectWithUserName', Mandatory=$true)]
    [switch]
    ${IncludeUserName}
  )

  if ($env:OS -ne 'Windows_NT') { Throw "This function runs on Windows only." }
  if (-not ${env:ProgramFiles(x86)}) { Throw "This function runs on 64-bit editions of Windows only."}

  # Define the helper type that provides access to the IsWow64Process 
  # Windows API function.
  # Calling this repeatedly in a session is idempotent, as long as the 
  # type definition doesn't change.
  Add-Type -MemberDefinition @'
    [DllImport("kernel32.dll")]
    public static extern bool IsWow64Process(System.IntPtr hProcess, [Out] out bool wow64Process);
'@ -Name NativeMethods -Namespace Kernel32

  [bool] $is32Bit = $False

  $isElevated = ([System.Security.Principal.WindowsPrincipal] [System.Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole('Administrators')
  if (-not $isElevated) {
    Write-Warning "Running without elevation: Output is limited to the current user's 32-bit processes."
  }

  # Pass the pipeline input / arguments through to Get-Process and collect all
  # resulting [System.Diagnostics.Process] instances.
  # Note that since we rely on inspecting the .Handle property of 
  # [System.Diagnostics.Process] instances, we don't support the -FileVersionInfo
  # and -Module parameters, because they output objects of different types.
  if ($MyInvocation.ExpectingInput) {
    # If there's pipeline input, we must remove the pipeline-binding parameters
    # from $PSBoundParameters to avoid a collisions.
    $null = foreach ($param in 'InputObject', 'Id', 'Name') {
      $PSBoundParameters.Remove($param)
    }
    $processes = $Input | Microsoft.PowerShell.Management\Get-Process @PSBoundParameters
  } else {
    $processes = Microsoft.PowerShell.Management\Get-Process @PSBoundParameters
  }

  # Now filter the result objects by removing non-32-bit processes.
  [bool] $is32Bit = $false
  foreach ($ps in $processes) {
      if (-not $ps.Handle) {
        # Without elevation, many processes cannot be accessed, and some
        # cannot even be accessed with elevation (e.g., 'services')
        Write-Verbose "Access to process handle denied: $($ps.Name) ($($ps.ID))"
      } elseif (-not ([Kernel32.NativeMethods]::IsWow64Process($ps.Handle, [ref]$is32Bit))) {
        Write-Error "IsWow64Process() Windows API call failed for ID $($ps.ID)" # should never happen
      } elseif ($is32Bit) { # a 32-bit process: output it
        $ps
      } else {
        Write-Verbose "Not a 32-bit process: $($ps.Name) ($($ps.ID))"
      }
  }

}

