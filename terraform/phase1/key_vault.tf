resource "azurerm_key_vault" "kv" {
name = "${var.prefix}-kv-${random_string.suffix.result}"
location = azurerm_resource_group.rg.location
resource_group_name = azurerm_resource_group.rg.name
tenant_id = data.azurerm_client_config.current.tenant_id
sku_name = "standard"
purge_protection_enabled = false
soft_delete_retention_days = 7
}


data "azurerm_client_config" "current" {}