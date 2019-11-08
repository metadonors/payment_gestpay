# Copyright 2019 Metadonors Srl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Payment Gestpay Acquirer',
    'summary': "Payment Acquirer: Gestpay Implementation",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Metadonors Srl, Agile Business Group,Odoo Community Association (OCA)',
    'website': 'https://www.metadonors.it',
    'installable': True,
    'depends': ['payment'],
    'data': [
        'security/payment_acquirer.xml',
        'views/payment_acquirer.xml',
        'views/payment_gestpay_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'demo': [
    ],
}
