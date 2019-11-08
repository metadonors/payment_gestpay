# -*- coding: utf-8 -*-
# Copyright 2017 Metadonors Srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models, _
from pygestpay import GestPAY

_logger = logging.getLogger('donodoo')

class PaymentToken(models.Model):

    _inherit = ['payment.token']

    def gestpay_create(self, values):
        if values.get('cc_number'):
            values['cc_number'] = values['cc_number'].replace(' ', '')
            acquirer_id = self.env['payment.acquirer'].browse(values['acquirer_id'])

            gestpay = GestPAY(acquirer_id.gestpay_shoplogin, test=acquirer_id.environment == 'test')
            exp_month, exp_year = values['cc_expiry'].split(" / ")
            
            token_data = gestpay.request_token(values['cc_number'], exp_month, exp_year)

            return {
                "acquirer_ref": token_data['Token'],
                "name": "XXXX XXXX XXXX %s - %s"  % (token_data['Token'][-4:], values['cc_holder_name'])
            }

        return {}
