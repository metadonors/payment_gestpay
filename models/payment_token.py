# -*- coding: utf-8 -*-
# Copyright 2017 Metadonors Srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models, _
from pygestpay import GestPAY

log = logging.getLogger('donodoo')

class PaymentToken(models.Model):

    _inherit = ['payment.token']
    