output "databricks_cluster_id" {
  value = databricks_cluster.low_cost.id
}

output "notebook_url" {
  value = "${var.databricks_host}/#notebook/${databricks_notebook.example.id}"
}