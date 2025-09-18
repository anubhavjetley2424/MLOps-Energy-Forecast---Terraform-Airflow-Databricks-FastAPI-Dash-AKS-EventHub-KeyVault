resource "databricks_cluster" "low_cost" {
  cluster_name            = var.cluster_name
  spark_version           = "13.3.x-scala2.12"
  node_type_id            = "Standard_DS3_v2"
  autotermination_minutes = 20
  num_workers = 1
}