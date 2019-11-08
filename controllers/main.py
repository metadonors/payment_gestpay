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

        acquirer = request.env.ref('payment_gestpay.payment_acquirer_gestpay')
        gestpay = GestPAY(acquirer.gestpay_shoplogin, test=acquirer.environment == 'test')
        url = gestpay.get_payment_page_url(**kwargs)

        return werkzeug.utils.redirect(url, 301)


    @http.route(['/payment/gestpay/register'], type='http', auth='public', csrf=False)
    def gestpay_payment_register(self, **kwargs):
        _logger.info("GESTPAY: Register payment")

        # TODO: manage errors and exceptions

        acquirer_id = request.env.ref('payment_gestpay.payment_acquirer_gestpay')
        gestpay = GestPAY(acquirer_id.gestpay_shoplogin, test=acquirer_id.environment == 'test')
        data = gestpay.decrypt(kwargs.get('b'))

        transaction_id = request.env['payment.transaction'].search([
            ('reference', '=', data['ShopTransactionID'])
        ])

        transaction_id._gestpay_s2s_validate_data(data)

        return werkzeug.utils.redirect('/payment/process')

    @http.route(['/payment/gestpay/s2s/create_json'], type='json', auth='public', csrf=False)
    def gestpay_s2s_create_json(self, **post):
        _logger.info("Gestpay S2S Create")
        error = ''
        acq = request.env['payment.acquirer'].browse(int(post.get('acquirer_id')))
        try:
            token = acq.s2s_process(post)
        except Exception as e:
            token = False
            error = str(e).splitlines()[0].split('|')[-1] or ''
        
        if not token:
            res = {
                'result': False,
                'error': error,
            }
            return res

        res = {
            'result': True,
            'id': token.id,
            'short_name': token.short_name,
            '3d_secure': False,
            'verified': False,
        }

        return res