from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class InvoiceGeneratorConfig(AppConfig):
    name = 'invoice_generator'
    verbose_name = _("Invoice Generator")
