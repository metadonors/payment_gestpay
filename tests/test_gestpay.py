# -*- coding: utf-8 -*-
import odoo
from odoo import fields
from odoo.addons.payment.tests.common import PaymentAcquirerCommon
from odoo.tools import mute_logger


class GestpayCommon(PaymentAcquirerCommon):

    def setUp(self):
        super(GestpayCommon, self).setUp()
        self.gestpay = self.env.ref('payment.payment_acquirer_gestpay')


@odoo.tests.tagged('post_install', '-at_install', '-standard', 'external')
class GestpayTest(StripeCommon):
    pass
    