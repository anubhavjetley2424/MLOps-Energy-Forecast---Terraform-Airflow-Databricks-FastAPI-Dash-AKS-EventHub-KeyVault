resource "azurerm_storage_account" "adls" {
  name                     = lower("${var.prefix}adls${random_string.suffix.result}")
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
  enable_https_traffic_only = true
}

resource "azurerm_storage_container" "raw" {
name = "raw"
storage_account_name = azurerm_storage_account.adls.name
container_access_type = "private"
}


resource "azurerm_storage_container" "processed" {
name = "processed"
storage_account_name = azurerm_storage_account.adls.name
container_access_type = "private"
}


resource "azurerm_storage_container" "predictions" {
name = "predictions"
storage_account_name = azurerm_storage_account.adls.name
container_access_type = "private"
}