# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://moylop.blogspot.com/
#    All Rights Reserved.
#    info moylop260 (moylop260@hotmail.com)
############################################################################
#    Coded by: moylop260 (moylop260@hotmail.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from report import report_sxw

from amount_to_text_es import amount_to_text as amount_to_text_class

amount_to_text_obj = amount_to_text_class()
#amount_to_text = amount_to_text_obj.amount_to_text
amount_to_text = amount_to_text_obj.amount_to_text_cheque

###sql_delete_report = "DELETE FROM ir_act_report_xml WHERE report_name = 'account.payment.voucher.receipt'"--Si no toma la actualizacion del reporte xml, borrarlo directamente desde la base de datos, con este script.
class voucher_receipt_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(voucher_receipt_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'set_address': self._set_address,
            'get_address': self._get_address,
            'amount_to_text': self._get_amount_to_text,
        })

    def _get_amount_to_text(self, amount, lang, currency=""):
        if currency.upper() in ('MXP', 'MXN', 'PESOS', 'PESOS MEXICANOS'):
            sufijo = 'M. N.'
            currency = 'PESOS'
        elif currency.upper() in ('GTQ', 'QUETZAL'):
            sufijo = ''
            currency = 'QUETZALES'
        else:
            sufijo = 'M. E.'
        #return amount_to_text(amount, lang, currency)
        amount_text = amount_to_text(amount, currency, sufijo)
        amount_text = amount_text and amount_text.upper() or ''
        return amount_text


    def _get_address(self):
        return self.address

    def _set_address(self, partner_id):
        partner_obj = self.pool.get('res.partner')
        partner_address_obj = self.pool.get('res.partner')
        address_id = partner_obj.address_get(self.cr, self.uid, [partner_id], ['invoice'])['invoice']
        address = partner_address_obj.browse(self.cr, self.uid, [address_id])[0]
        self.address = address
        #return address
        return ""

report_sxw.report_sxw('report.account.payment.voucher.receipt', 'account.invoice', 'addons/account_invoice_receipt/report/voucher_receipt_report.rml', parser=voucher_receipt_report, header=False)
