#!/usr/bin/env python3
import os.path

from django.template.loader import get_template
from weasyprint import HTML

from .models import *


BASE_PATH = os.path.join(os.path.dirname(__file__))
BASE_URL = os.path.join(BASE_PATH, 'templates')


def generate_pdf(
        currency: str, invoice: Invoice,
        template=None, static_path=BASE_URL):

    if not template:
        template = get_template('index.html')

    ctx = dict(
        invoice=invoice,
        order=invoice.order,
        currency=currency,
        executive=invoice.vendor.executive,
        vendor=invoice.vendor,
        billing_address=invoice.billing_address,
    )

    html_text = template.render(ctx)
    weasytemplate = HTML(string=html_text, base_url=static_path)

    return weasytemplate
