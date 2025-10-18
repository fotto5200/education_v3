$ErrorActionPreference = 'Stop'

# Base API URL
$Base = 'http://localhost:8000'

# Create a web session to persist cookies (httpOnly session cookie)
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

Write-Host '=== Selection Test ==='

# 1) Start session and capture CSRF (not needed for GET test, but useful to display)
try {
  $sess = Invoke-RestMethod -Uri "$Base/api/session" -Method Post -WebSession $session
  Write-Host ("Session started: {0}" -f $sess.session_id)
} catch {
  Write-Host 'Failed to create session'; throw
}

# 2) Fetch a sequence of items to verify no immediate repeats and type-aware rotation
Write-Host 'Fetching 10 items via /api/item/next ...'
for ($i = 1; $i -le 10; $i++) {
  $resp = Invoke-RestMethod -Uri "$Base/api/item/next" -WebSession $session
  $id = $resp.item.id
  $type = $resp.item.type
  Write-Host ("{0,2}: id={1} type={2}" -f $i, $id, $type)
}

# 3) Optional: demonstrate type override using the last observed type (if any)
if ($null -ne $type -and "$type" -ne '') {
  Write-Host ("\nOverride type once: ?type={0}" -f $type)
  $override = Invoke-RestMethod -Uri ("$Base/api/item/next?type={0}" -f [uri]::EscapeDataString($type)) -WebSession $session
  Write-Host (" -> id={0} type={1}" -f $override.item.id, $override.item.type)
}

Write-Host '=== Done ==='
