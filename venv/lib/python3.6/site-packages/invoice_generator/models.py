from datetime import date as dt_date
from typing import Tuple


BOTTOM_ROW_COUNT = 6


class Address(object):
    __slots__ = ('name', 'street', 'postcode', 'city')

    def __init__(self, name, street, postcode, city):
        self.name = name
        self.street = street
        self.postcode = postcode
        self.city = city


class Executive(object):
    __slots__ = ('name', 'text')

    def __init__(self, name, text):
        self.name = name
        self.text = text


class Vendor(object):
    __slots__ = ('executive', 'address', 'vat_number', 'additional_text')

    def __init__(
            self, executive: Executive, address: Address,
            vat_number: str, additional_text: tuple):

        self.executive = executive
        self.address = address
        self.vat_number = vat_number
        self.additional_text = additional_text

    @property
    def additional_text_suffix(self):
        res = BOTTOM_ROW_COUNT - len(self.additional_text)
        return '"\\a" ' * res


class Order(object):
    __slots__ = (
        'order_id', 'customer_id', 'date',
        'pay_until_date', 'shipping_date_range',
        'tax_rate', 'total_discounted', 'total_shipping_net',
        'total_tax', 'total_net', 'total_gross'
    )

    def __init__(self, invoice_id, customer_id, date,
                 payment_date_limit,
                 shipping_date_range: Tuple[dt_date, dt_date],
                 tax_rate, total_discounted, total_shipping_net,
                 total_tax, total_net, total_gross):
        self.order_id = invoice_id
        self.customer_id = customer_id
        self.date = date
        self.pay_until_date = payment_date_limit
        self.shipping_date_range = shipping_date_range
        self.tax_rate = tax_rate

        self.total_discounted = total_discounted
        self.total_shipping_net = total_shipping_net

        self.total_tax = total_tax
        self.total_net = total_net
        self.total_gross = total_gross

    @property
    def shipping_from(self):
        return self.shipping_date_range[0]

    @property
    def shipping_to(self):
        return self.shipping_date_range[1]


class OrderItem(object):
    __slots__ = (
        'reference', 'text', 'quantity', 'net_price', 'tax_rate',
        'total_net',
    )

    def __init__(self, order: Order,
                 reference, name: str, quantity: int,
                 net_price: float, total_net: float,
                 tax_rate: float = None):

        self.reference = reference
        self.total_net = total_net

        self.text = name
        self.quantity = quantity
        self.net_price = net_price

        if not tax_rate:
            tax_rate = order.tax_rate
        self.tax_rate = tax_rate


class Invoice(object):
    __slots__ = ('order', 'vendor', 'billing_address', 'items')

    def __init__(self, order_data: Order,
                 vendor: Vendor, billing_address: Address,
                 items: OrderItem):
        self.order = order_data
        self.vendor = vendor
        self.billing_address = billing_address
        self.items = items


__all__ = ('Address', 'Vendor', 'Order', 'OrderItem', 'Invoice')
