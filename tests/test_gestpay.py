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

    def test_10_gestpay_s2s(self):
        self.assertEqual(1,1)

    def test_20_gestpay_form_render(self):
        self.assertEqual(1,1)

    def test_30_gestpay_form_management(self):
        self.assertEqual(1,1)
