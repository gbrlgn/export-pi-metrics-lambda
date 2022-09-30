data "archive_file" "create_dist_pkg" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_function"
  output_path = "${path.module}/lambda_function.zip"
}

resource "aws_lambda_function" "export_pi_metrics" {
  function_name = "export-pi-metrics-${var.env}"
  role          = aws_iam_role.export_pi_metrics_role.arn
  handler       = "export_pi.lambda_handler"
  filename      = data.archive_file.create_dist_pkg.output_path
  runtime       = "python3.9"
  timeout       = 60
  tags          = { Environment = var.env }
}

resource "aws_lambda_permission" "export_pi_metrics_invoke" {
  statement_id  = "AllowExecutionFromCloudWatchStart"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.export_pi_metrics.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.export_pi_metrics_start.arn
}

output "arn" {
  value = aws_lambda_function.export_pi_metrics.arn
}
