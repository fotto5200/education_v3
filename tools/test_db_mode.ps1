param(
  [string]$Base = 'http://localhost:8000',
  [string]$Type = 'TYPE_A',
  [int]$Attempts = 5
)

$ErrorActionPreference = 'Stop'

$ws   = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$sess = Invoke-RestMethod -Uri "$Base/api/session" -Method Post -WebSession $ws
$csrf = $sess.csrf_token
Write-Host "Session: $($sess.session_id)"

for ($i=1; $i -le $Attempts; $i++) {
  $item = Invoke-RestMethod -Uri "$Base/api/item/next?type=$Type" -WebSession $ws
  $step = $item.item.steps[0]
  # Try correct choice '5' when present; else first choice
  $c = ($step.choices | Where-Object { $_.text -eq '5' } | Select-Object -First 1)
  if (-not $c) { $c = $step.choices[0] }
  $body = @{ session_id=$item.session_id; item_id=$item.item.id; step_id=$step.step_id; choice_id=$c.id } | ConvertTo-Json -Compress
  $res  = Invoke-RestMethod -Uri "$Base/api/answer" -Method Post -WebSession $ws -Headers @{ 'X-CSRF-Token'=$csrf } -ContentType 'application/json' -Body $body
  $label = if ($res.correct) { 'Correct' } else { 'Incorrect' }
  Write-Host ("{0,2}: {1}" -f $i, $label)
  Start-Sleep -Milliseconds 200
}

Write-Host "\nProgress:"
$progress = Invoke-RestMethod -Uri "$Base/api/progress" -WebSession $ws
$progress | ConvertTo-Json -Depth 5

Write-Host "\nCSV Preview:"
Invoke-RestMethod -Uri "$Base/api/events.csv" -WebSession $ws | Out-String | Select-Object -First 1
