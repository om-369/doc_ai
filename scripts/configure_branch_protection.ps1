# Configure branch protection rules
$owner = "om-369"
$repo = "post3"
$branch = "master"

$headers = @{
    Authorization = "token $env:GITHUB_TOKEN"
    Accept = "application/vnd.github.v3+json"
}

$body = @{
    required_status_checks = @{
        strict = $true
        contexts = @("test", "deploy-staging")
    }
    enforce_admins = $true
    required_pull_request_reviews = @{
        dismissal_restrictions = @{}
        dismiss_stale_reviews = $true
        require_code_owner_reviews = $true
        required_approving_review_count = 1
    }
    restrictions = $null
} | ConvertTo-Json

$uri = "https://api.github.com/repos/$owner/$repo/branches/$branch/protection"

Invoke-RestMethod -Uri $uri -Method Put -Headers $headers -Body $body -ContentType "application/json"
