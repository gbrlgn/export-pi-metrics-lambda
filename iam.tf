resource "aws_iam_role" "export_pi_metrics_role" {
  name = "export_pi_metrics_role"
}

resource "aws_iam_role_policy" "export_pi_metrics_policy" {
  name = "export_pi_metrics_policy"
  role = aws_iam_role.export_pi_metrics_role.name

  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "pi:GetResourceMetrics"
        ],
        "Effect": "Allow",
        "Resource": "arn:aws:pi:*:*:metrics/rds/*"
      }
    ]
  }
  EOF
}

resource "aws_iam_role_policy_attachment" "cw_full_access" {
  role       = aws_iam_role.export_pi_metrics_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchFullAccess"
}

resource "aws_iam_role_policy_attachment" "rds_read_only_access" {
  role       = aws_iam_role.export_pi_metrics_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSReadOnlyAccess"
}