variable "databricks_host" {
  description = "The Databricks workspace URL (e.g., https://adb-xxxx.x.azuredatabricks.net)"
  type        = string
}

variable "databricks_token" {
  description = "Databricks personal access token"
  type        = string
  sensitive   = true
}

variable "cluster_name" {
  description = "Name for the Databricks cluster"
  type        = string
  default     = "mlops-cluster"
}