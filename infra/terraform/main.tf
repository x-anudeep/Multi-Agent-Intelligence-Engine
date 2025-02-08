resource "google_artifact_registry_repository" "maie" {
  location      = var.region
  repository_id = var.artifact_registry_repository
  description   = "Container images for the Multi-Agent Intelligence Engine"
  format        = "DOCKER"
}

resource "google_container_cluster" "maie" {
  name                     = var.cluster_name
  location                 = var.region
  remove_default_node_pool = true
  initial_node_count       = 1

  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
}

resource "google_container_node_pool" "maie_primary" {
  name       = "${var.cluster_name}-primary"
  cluster    = google_container_cluster.maie.name
  location   = var.region
  node_count = var.node_count

  node_config {
    machine_type = "e2-standard-4"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

