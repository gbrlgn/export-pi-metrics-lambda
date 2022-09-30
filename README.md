# export-pi-metrics-lambda

This Terraform module deploys a AWS Lambda function to export Performance Insights metrics from RDS databases into CloudWatch.

The following resources will be created:
- AWS Lambda function 
- CloudWatch/EventBridge event rule and target
- IAM role

## Usage
```hcl
module "export_pi_metrics" {
    for_each    = { for metrics in local.workspace.export_pi_metrics : metrics.name => metrics }
    source      = "./export-pi-metrics-lambda"
    enabled     = each.value.enabled
    env         = each.value.env
}
```

## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

No modules.