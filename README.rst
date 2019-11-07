.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3


# Payment Gestpay

Payment Acquirer: Gestpay Implementation

## Installation

To install this module, you need to:

* Go to Invoicing -> Configuration -> Payment Acquirers
* Install Gestpay Acquirer
* Activate Gestpay Acquirer

## Configuration

To configure this module, you need to:

* Go to Invoicing -> Configuration -> Payment Acquirers
* Select Gestpay Acquirer
* Set your Gestpay Shop Id

On Gestpay backend you should set the url where users will be redirected after payments (see (Axerve docs)[https://docs.gestpay.it/soap/pay/using-banca-sella-payment-page/])

* Go to Configuration -> Environment -> Response Addresses
* Se both positive and negative URL as <your_odoo_url>/payment/gestpay/regiter

.. figure:: path/to/local/image.png
   :alt: alternative description
   :width: 600 px

## Usage

To use this module, you need to:

* Buy something in your Shop
* Select Gestpay as payment gateway

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

## Known issues / Roadmap

* Improve error and exceptions handle in external payment page process
* Implement S2S form payment
* Support card tokenization (remember me feature)


## Bug Tracker

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

## Credits

### Images

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

###Contributors

* Fabrizio Arzeni <fabrizio.arzeni@metadonors.it>
* Simone Rubino <simone.rubino@agilebg.com>

### Funders

The development of this module has been financially supported by:

* [Metadonors](https://www.metadonors.it)
* [Agile Business Group](https://www.agilebg.com/page/homepage)

### Maintainer

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
