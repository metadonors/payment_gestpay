# -*- coding: utf-8 -*-
import logging
import werkzeug

from odoo import http
from odoo.http import request
from odoo.addons.payment.controllers.portal import PaymentProcessing

from pygestpay import GestPAY

_logger = logging.getLogger(__name__)


class GestpayController(http.Controller):

    # TOFIX: no csrf, public route...something bad could happen
    @http.route(['/payment/gestpay/redirect'], type='http', auth='public', csrf=False)
    def gestpay_redirect(self, **kwargs):
        _logger.info("GESTPAY: Redirecting to payment page")

        # TODO: manage errors and exceptions

        # TO FIX: maybe there is a better way to retrieve gestpay acquirer?
        acquirer = request.env.ref('payment_gestpay.payment_acquirer_gestpay')
        gestpay = GestPAY(acquirer.gestpay_shoplogin, test=acquirer.environment == 'test')
        url = gestpay.get_payment_page_url(**kwargs)

        return werkzeug.utils.redirect(url, 301)


    @http.route(['/payment/gestpay/register'], type='http', auth='public', csrf=False)
    def gestpay_payment_register(self, **kwargs):
        _logger.info("GESTPAY: Register payment")

        # TODO: manage errors and exceptions

        # TO FIX: maybe there is a better way to retrieve gestpay acquirer?
        acquirer_id = request.env.ref('payment_gestpay.payment_acquirer_gestpay')
        gestpay = GestPAY(acquirer_id.gestpay_shoplogin, test=acquirer_id.environment == 'test')
        data = gestpay.decrypt(kwargs.get('b'))

        transaction_id = request.env['payment.transaction'].search([
            ('reference', '=', data['ShopTransactionID'])
        ])

        transaction_id._gestpay_s2s_validate_data(data)

        _logger.error(data)


        return werkzeug.utils.redirect('/payment/process')
