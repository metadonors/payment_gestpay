# -*- coding: utf-8 -*-
# Copyright 2017 Metadonors Srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.queue_job.job import job
from datetime import date, timedelta, datetime
from dateutil import relativedelta
from pygestpay import GestPAY
import pycard
import logging

log = logging.getLogger('donodoo')

CARD_TYPES = [
    ('American Express', ['34', '37']),
    ('China UnionPay', ['88']),
    ('Diners Club', ['30', '36', '38', '39']),
    ('Discover', ['60', '62', '64', '65']),
    ('JCB', ['35']),
    ('Maestro', ['50', '63', '67']),
    ('MasterCard', ['51', '52', '53', '54', '55']),
    ('Visa', ['4']),
]


class PaymentToken(models.Model):

    _inherit = ['payment.token']

    gestpay_creditcard_type = fields.Char(string=_("Card Type"), compute='_compute_card_name', store=True)
    gestpay_creditcard_prefix = fields.Char(string=_("Number Prefix"), help="Credit Card Number Prefix")
    gestpay_creditcard_number = fields.Char(string=_("Number"), help="Credit Card Number", track_visibility='onchange')
    gestpay_creditcard_exp_month = fields.Char(string=_("Month Expiration"), track_visibility='onchange')
    gestpay_creditcard_exp_year = fields.Char(string=_("Year Expiration"), track_visibility='onchange')
    gestpay_creditcard_ccv = fields.Char(string=_("CCV"), track_visibility='onchange')

    gestpay_creditcard_exp_date = fields.Date(string="Expiration Date", readonly=True, compute="_compute_expiration_date", store=True)

    keep_clear = fields.Boolean(string=_("Avoid tokenization"), default=True)

    provider = fields.Char(string=_("Payment Provider"), compute="_compute_provider", store=True, track_visibility='onchange')

    months_since_expiration = fields.Integer(string=_("Months since expiration"), compute="_compute_expiration_months", search="_search_expiration_months", readonly=True)

    name = fields.Char(compute="_compute_card_name", store=True)

    acquirer_ref = fields.Char('Acquirer Token', required=False)

    def compute_card_name(self):
        self._compute_card_name()
        
    @api.depends("gestpay_creditcard_number", "acquirer_ref")
    def _compute_card_name(self):
        for record in self:
            if record.gestpay_creditcard_number:
                card = pycard.Card(number=record.gestpay_creditcard_number, month=1, year=2030, cvc=123)
                record.name = 'XXXXXXXXXXXX%s' % (record.gestpay_creditcard_number[-4:])
                record.gestpay_creditcard_type = card.friendly_brand
            elif record.acquirer_ref:

                record.name = 'XXXXXXXXXXXX%s' % (record.acquirer_ref[-4:])
                record.gestpay_creditcard_type = "Sconosciuto"
                for ctype, prefixes in CARD_TYPES:
                    for prefix in prefixes:
                        if record.acquirer_ref.startswith(prefix):
                            record.gestpay_creditcard_type = ctype
                            break
                    
                    if record.gestpay_creditcard_type != "Sconosciuto":
                        break

            else:
                record.name = "Invalid credit card"

    @api.depends("acquirer_id")
    def _compute_provider(self):
        for token in self:
            token.provider = token.acquirer_id.provider


    @api.constrains('gestpay_creditcard_number', 'gestpay_creditcard_exp_month', 'gestpay_creditcard_exp_year')
    def _check_credit_card_number(self):
        log.debug("Checking Credit Card")
        for record in self:
            if record.gestpay_creditcard_number and not record.acquirer_ref:
                if not record.gestpay_creditcard_exp_month or not record.gestpay_creditcard_exp_year:
                    raise ValidationError(_("Invalid Credit card expiration"))
                if not record.gestpay_creditcard_exp_month.isdigit() or not record.gestpay_creditcard_exp_year.isdigit():
                    raise ValidationError(_("Invalid Credit card expiration"))
                    
                exp_year = int(record.gestpay_creditcard_exp_year)
                if exp_year < 2000:
                    exp_year += 2000
                card = pycard.Card(number=record.gestpay_creditcard_number, 
                                   month=int(record.gestpay_creditcard_exp_month), 
                                   year=exp_year, 
                                   cvc=123)
                log.debug("Card %s is valid %s" % (record.gestpay_creditcard_number, card.is_valid))
                if not card.is_mod10_valid or not record.gestpay_creditcard_number.isdigit():
                    raise ValidationError(_("Credit card number is not valid"))
                if card.is_expired:
                    raise ValidationError(_("Credit card is expired"))

    def gestpay_creditcard_exp(self):
        return "%s/%s" % (self.gestpay_creditcard_exp_month, self.gestpay_creditcard_exp_year)


    @api.depends("gestpay_creditcard_exp_month", "gestpay_creditcard_exp_year")
    def _compute_expiration_date(self):
        for card in self:
            try:
                if len(card.gestpay_creditcard_exp_year) == 2:
                    exp_year = int("20%s" % card.gestpay_creditcard_exp_year)
                elif len(card.gestpay_creditcard_exp_year) == 4:
                    exp_year = int(card.gestpay_creditcard_exp_year)
                else:
                    continue
            except:
                continue

            try:
                exp_month = int(card.gestpay_creditcard_exp_month)
            except:
                continue


            card.gestpay_creditcard_exp_date = date(exp_year, exp_month, 1)


    @api.depends("gestpay_creditcard_exp_date")
    def _compute_expiration_months(self):
        for card in self:
            exp_date = card.gestpay_creditcard_exp_date

            delta = relativedelta.relativedelta(date.today(), exp_date)
            card.months_since_expiration = delta.months

    def _search_expiration_months(self, operator, value):
        d = date.today() - relativedelta.relativedelta(months=value)

        if operator == "=":
            fdm = date(d.year, d.month, 1)
            ldm = fdm + relativedelta.relativedelta(months=1,days=-1)
            domain = [('gestpay_creditcard_exp_date', '>=', fdm), ('gestpay_creditcard_exp_date', '<=', ldm)]
        else:
            domain = [('gestpay_creditcard_exp_date', operator, d)]

        x = self.search(domain)

        print(domain)
        
        return [('id', 'in', x.ids)]

    @api.multi
    @job
    def fake_tokenize(self):
        for record in self:
            acquirer = record.acquirer_id
            partner = record.partner_id
            gestpay = GestPAY(acquirer.gestpay_shoplogin, test=acquirer.environment == 'test')

            if not record.gestpay_creditcard_number: continue
            exp_year = record.gestpay_creditcard_exp_year if len(record.gestpay_creditcard_exp_year) == 2 else record.gestpay_creditcard_exp_year[2:]

            data = gestpay.request_token(record.gestpay_creditcard_number, 
                                            record.gestpay_creditcard_exp_month,
                                            exp_year)
            
            if data['TransactionResult'] == "OK":
                backup = {}
                backup['name'] = data['Token']
                backup['token'] = data['Token']
                backup['number'] = record.gestpay_creditcard_number
                backup['exp_month'] = record.gestpay_creditcard_exp_month
                backup['exp_year'] = record.gestpay_creditcard_exp_year
                self.env['payment.token.backup'].create(backup)

    @api.multi
    def tokenize(self):
        for record in self:
            acquirer = record.acquirer_id
            partner = record.partner_id
            gestpay = GestPAY(acquirer.gestpay_shoplogin, test=acquirer.environment == 'test')

            if not record.gestpay_creditcard_number: continue
            exp_year = record.gestpay_creditcard_exp_year if len(record.gestpay_creditcard_exp_year) == 2 else record.gestpay_creditcard_exp_year[2:]

            data = gestpay.request_token(record.gestpay_creditcard_number, 
                                            record.gestpay_creditcard_exp_month,
                                            exp_year)
            
            if data['TransactionResult'] == "OK":
                values = {}
                values['gestpay_creditcard_number'] = ''
                values['acquirer_ref'] = data['Token']
                values['keep_clear'] = False
                record.write(values)

                backup = {}
                backup['name'] = data['Token']
                backup['token'] = data['Token']
                backup['number'] = record.gestpay_creditcard_number
                backup['exp_month'] = record.gestpay_creditcard_exp_month
                backup['exp_year'] = record.gestpay_creditcard_exp_year
                self.env['payment.token.backup'].create(backup)



    @api.multi
    def write(self, vals):
        super(PaymentToken, self).write(vals)

        if 'keep_clear' in vals and not vals['keep_clear']:
            self.tokenize()

    @api.model
    def gestpay_create(self, values):
        if values.get('gestpay_creditcard_number'):
            acquirer = self.env['payment.acquirer'].browse(values['acquirer_id'])
            partner = self.env['res.partner'].browse(values['partner_id'])
            gestpay = GestPAY(acquirer.gestpay_shoplogin, test=acquirer.environment == 'test')

            
            if ('keep_clear' not in values.keys() or not values['keep_clear']):
                exp_year = values['gestpay_creditcard_exp_year'] if len(values['gestpay_creditcard_exp_year']) == 2 else values['gestpay_creditcard_exp_year'][2:]
                data = gestpay.request_token(values['gestpay_creditcard_number'], 
                                             values['gestpay_creditcard_exp_month'],
                                             exp_year)
                
                if data['TransactionResult'] == "OK":
                    backup = {}
                    backup['name'] = data['Token']
                    backup['token'] = data['Token']
                    backup['number'] = values['gestpay_creditcard_number']
                    backup['exp_month'] = values['gestpay_creditcard_exp_month']
                    backup['exp_year'] = values['gestpay_creditcard_exp_year']
                    self.env['payment.token.backup'].create(backup)

                    values['gestpay_creditcard_number'] = ''
                    values['acquirer_ref'] = data['Token']
            

                
        return values
