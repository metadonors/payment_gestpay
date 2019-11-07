# -*- coding: utf-8 -*-
# Copyright 2017 Metadonors Srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import  logging

from odoo import api, fields, models, _
from pygestpay import GestPAY
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger('donodoo')

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    error_code = fields.Char(string=_("Error code"))

    def gestpay_compute_fees(self, amount, currency, country):
        return 0
    
    def _gestpay_get_client(self):
        return GestPAY(self.acquirer_id.gestpay_shoplogin, test=self.acquirer_id.environment == 'test')

    def _gestpay_prepare_transaction_vals(self):
        vals = {}

        vals['amount'] = self.amount
        vals['transaction_id'] = self.reference
        vals['buyer_name'] = self.payment_token_id.partner_id.name
        vals['buyer_email'] = self.payment_token_id.partner_id.email
        vals['token'] = self.payment_token_id.acquirer_ref
        
        return vals
    
    @api.multi
    def _gestpay_s2s_validate_data(self, data):
        self.ensure_one()

        if data['TransactionResult'] == "OK":
            self.write({
                    'state': 'done',
                    'acquirer_reference': data['BankTransactionID'],
                    'date': fields.Datetime.now(),
                })
            self._set_transaction_done()
            self.execute_callback()
            if self.payment_token_id:
                self.payment_token_id.verified = True
            return True
        else:
            self.write({
                    'date': fields.datetime.now(),
                    'state_message': "%s (%s)" % (data['ErrorDescription'], data['ErrorCode']),
                })
            self._set_transaction_cancel()
            return False

    @api.multi
    def gestpay_s2s_do_transaction(self, **kwargs):
        self.ensure_one()

        pay_args = self._gestpay_prepare_transaction_vals()
        gestpay = self._gestpay_get_client()
        data = gestpay.token_transaction(**pay_args)

        return self._gestpay_s2s_validate_data(data)

    @api.multi
    def gestpay_s2s_capture_transaction(self, **kwargs):
        return True
    
    def _gestpay_prepare_refund_vals(self):
        vals = {}
        
        vals['amount'] = self.amount
        vals['transaction_id'] = self.acquirer_reference
        vals['bank_transaction_id'] = self.reference

        return vals

    @api.multi
    def gestpay_s2s_do_refund(self, **kwargs):
        self.ensure_one()

        refund_vals = self._gestpay_prepare_refund_vals()
        gestpay = self._gestpay_get_client()
        data = gestpay.refund_transaction(**refund_vals)

        return self._gestpay_s2s_validate_data(data)