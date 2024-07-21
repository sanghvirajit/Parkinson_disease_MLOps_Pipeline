resource "aws_ecr_repository" "repo" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }

  force_delete = true
}

output "image_uri" {
  value     = "${aws_ecr_repository.repo.repository_url}:${var.ecr_image_tag}"
}