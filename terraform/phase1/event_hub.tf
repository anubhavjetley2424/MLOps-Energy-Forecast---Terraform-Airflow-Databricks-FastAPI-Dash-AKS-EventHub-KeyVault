resource "azurerm_eventhub_namespace" "eh_ns" {
name = "${var.prefix}-eh-ns-${random_string.suffix.result}"
location = azurerm_resource_group.rg.location
resource_group_name = azurerm_resource_group.rg.name
sku = "Standard"
capacity = 1
}


resource "azurerm_eventhub" "eh" {
name = "ingest"
namespace_name = azurerm_eventhub_namespace.eh_ns.name
resource_group_name = azurerm_resource_group.rg.name
partition_count = 4
message_retention = 1
}