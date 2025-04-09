# data "template_file" "collector_yaml_config" {
#   template = file("${path.module}/app/src/collector-template.yaml.tpl")
#
#   vars = {
#     otlp_endpoint = "${data.aws_lb.nlb.dns_name}/alloy"
#   }
# }
#
# resource "local_file" "rendered_collector_yaml" {
#   filename = "${path.module}/app/src/collector.yaml"
#   content  = data.template_file.collector_yaml_config.rendered
# }
