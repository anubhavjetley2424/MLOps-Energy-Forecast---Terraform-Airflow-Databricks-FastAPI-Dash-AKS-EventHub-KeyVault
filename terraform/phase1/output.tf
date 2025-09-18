output "resource_group" {
value = azurerm_resource_group.rg.name
}


output "adls_account" {
value = azurerm_storage_account.adls.name
}


output "eventhub_namespace" {
value = azurerm_eventhub_namespace.eh_ns.name
}


output "aks_cluster_name" {
value = azurerm_kubernetes_cluster.aks.name
}


output "acr_name" {
value = azurerm_container_registry.acr.name
}


output "databricks_workspace" {
value = azurerm_databricks_workspace.dbx.workspace_url
}
