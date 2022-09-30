resource "aws_cloudwatch_event_rule" "export_pi_metrics_start" {
  name                = "export-pi-metrics-start-${var.env}"
  schedule_expression = "rate(5 minutes)"
  is_enabled          = var.enabled
  tags                = { Environment = var.env }
}

resource "aws_cloudwatch_event_target" "export_pi_metrics_start_target" {
  rule      = aws_cloudwatch_event_rule.export_pi_metrics_start.name
  target_id = "export-pi-metrics-start-${var.env}"
  arn       = aws_lambda_function.export_pi_metrics.arn

  input = <<EOI
    {
      "action": "start"
    }
    EOI
}