# Create 20 test tasks
$topics = @(
  "Quarterly report", "System monitoring update", "1C integration",
  "Backup setup", "API testing", "Process documentation",
  "Database optimization", "Server migration", "Team training", "Security check",
  "Dashboard development", "CI/CD setup", "Log analysis", "Performance tuning",
  "Metrics implementation", "License inventory", "Audit prep", "Code refactoring",
  "Application deployment", "Failover testing"
)

$statuses = @("Started", "In progress", "Review", "Done", "Waiting", "Rework")
$priorities = @("high", "medium", "low")
$states = @("in_progress", "postponed", "closed")
$executorIds = @(2, 6, 7, 8)  # IDs from API

$base = "http://localhost:8000/api/items"

Write-Host "Creating 20 test tasks..." -ForegroundColor Green

for ($i = 1; $i -le 20; $i++) {
  $topic = ($topics | Get-Random) + " #$i"
  $priority = $priorities | Get-Random
  $state = $states | Get-Random
  $ticket = "TASK-$(1001 + $i)"
  $status_note = $statuses | Get-Random
  $execId = $executorIds | Get-Random
  $daysOffset = Get-Random -Minimum -10 -Maximum 30
  $due_date = (Get-Date).AddDays($daysOffset).ToString("yyyy-MM-dd")

  $body = @{
    topic = $topic
    priority = $priority
    state = $state
    ticket = $ticket
    due_date = $due_date
    executors = @($execId)
  } | ConvertTo-Json

  try {
    $response = Invoke-WebRequest -Uri $base -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop -UseBasicParsing
    if ($response.StatusCode -eq 200) {
      $data = $response.Content | ConvertFrom-Json
      Write-Host "[$i/20] OK $ticket" -ForegroundColor Green

      # Add random status (50% chance)
      if ((Get-Random -Minimum 0 -Maximum 100) -gt 50) {
        $statusDate = (Get-Date).AddDays((Get-Random -Minimum -3 -Maximum 0)).ToString("yyyy-MM-dd")
        $status_body = @{
          status_date = $statusDate
          status_note = $status_note
        } | ConvertTo-Json

        Invoke-WebRequest -Uri "$base/$($data.id)/statuses" -Method POST -Body $status_body -ContentType "application/json" -ErrorAction Stop -UseBasicParsing | Out-Null
      }
    }
  }
  catch {
    $err = $_.Exception.Message
    Write-Host "[$i/20] ERROR: $err" -ForegroundColor Red
  }

  Start-Sleep -Milliseconds 150
}

Write-Host "`nDone! Refresh the page in browser." -ForegroundColor Cyan
