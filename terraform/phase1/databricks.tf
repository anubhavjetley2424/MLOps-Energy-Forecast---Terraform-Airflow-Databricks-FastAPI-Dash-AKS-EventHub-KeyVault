resource "azurerm_databricks_workspace" "dbx" {
  name                        = "${var.prefix}-dbx-${random_string.suffix.result}"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  managed_resource_group_name = "${var.prefix}-dbx-mrg-${random_string.suffix.result}"
  sku                         = "standard"
  depends_on                  = [azurerm_resource_group.rg]
}