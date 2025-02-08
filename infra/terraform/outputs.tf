output "artifact_registry_repository_url" {
  description = "Artifact Registry repository path."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.maie.repository_id}"
}

output "gke_cluster_name" {
  description = "Provisioned GKE cluster name."
  value       = google_container_cluster.maie.name
}

output "gke_cluster_endpoint" {
  description = "Provisioned GKE cluster endpoint."
  value       = google_container_cluster.maie.endpoint
}

