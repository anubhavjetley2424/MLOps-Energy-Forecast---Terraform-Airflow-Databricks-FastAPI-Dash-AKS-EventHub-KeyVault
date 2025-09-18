resource "azurerm_kubernetes_cluster" "aks" {
name = "${var.prefix}-aks-${random_string.suffix.result}"
location = azurerm_resource_group.rg.location
resource_group_name = azurerm_resource_group.rg.name
dns_prefix = "${var.prefix}-aks"


default_node_pool {
name = "agentpool"
vm_size = "Standard_D4s_v3"
node_count = 2
}


identity {
type = "SystemAssigned"
}


network_profile {
network_plugin = "azure"
dns_service_ip = "10.2.0.10"
service_cidr = "10.2.0.0/16"

}
}


# Grant AKS access to ACR
resource "azurerm_role_assignment" "acr_pull" {
scope = azurerm_container_registry.acr.id
role_definition_name = "AcrPull"
principal_id = azurerm_kubernetes_cluster.aks.identity[0].principal_id
}