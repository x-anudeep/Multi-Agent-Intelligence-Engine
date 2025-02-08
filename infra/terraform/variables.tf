variable "project_id" {
  description = "Google Cloud project id."
  type        = string
}

variable "region" {
  description = "Primary Google Cloud region."
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE cluster name for the MAIE platform."
  type        = string
  default     = "maie-gke"
}

variable "artifact_registry_repository" {
  description = "Artifact Registry repository name for MAIE images."
  type        = string
  default     = "maie-images"
}

variable "node_count" {
  description = "Initial node count for the GKE node pool."
  type        = number
  default     = 2
}

