resource "databricks_notebook" "example" {
  path       = "/Shared/energy_forecast"
  source     = "./notebook/forecast.py"
  depends_on = [databricks_cluster.low_cost]
}