# create required folder structure just in case
New-Item -ItemType Directory -Path ".\data\logs" -Force
New-Item -ItemType Directory -Path ".\data\raw" -Force
New-Item -ItemType Directory -Path ".\data\processed" -Force
New-Item -ItemType Directory -Path ".\data\model" -Force
New-Item -ItemType Directory -Path ".\data\postgres" -Force

# for the presentation, create empty log files
New-Item -ItemType File -Path ".\data\logs\data_retrieval.log" -Force
New-Item -ItemType File -Path ".\data\logs\transform.log" -Force
New-Item -ItemType File -Path ".\data\logs\model_creation.log" -Force
New-Item -ItemType File -Path ".\data\logs\api.log" -Force

Get-Content .env | ForEach-Object {
    $line = $_.Trim()
    if (-not [string]::IsNullOrEmpty($line) -and -not $line.StartsWith("#")) {
        $parts = $line.Split('=')
        $key = $parts[0].Trim()
        $value = $parts[1].Trim()
        Invoke-Expression "`$env:$key = `$value"
    }
}


# start database
docker-compose up -d jobmarket_db

# set PIPELINE_ACTION for setup phase
$env:PIPELINE_ACTION = "init"
# start initial data retrieval process
docker-compose up -d jobmarket_data_retrieval

# when data retrieval is complete, start transform
docker wait jobmarket_data_retrieval_container
docker-compose up -d jobmarket_transform

# when transform is complete, start model creation
docker wait jobmarket_transform_container
docker-compose up -d jobmarket_model

# when model creation is complete, start api
docker wait jobmarket_model_container
docker-compose up -d jobmarket_api

Write-Host "Setup phase finished"
