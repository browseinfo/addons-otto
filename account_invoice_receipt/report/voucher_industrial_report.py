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

#DELETE FROM ir_act_report_xml WHERE report_name = 'account.payment.voucher.industrial'

import time

months_selection = [
        (1,'Enero'),
        (2,'Febrero'),
        (3,'Marzo'),
        (4,'Abril'),
        (5,'Mayo'),
        (6,'Junio'),
        (7,'Julio'),
        (8,'Agosto'),
        (9,'Septiembre'),
        (10,'Octubre'),
        (11,'Noviembre'),
        (12,'Diciembre'),
    ]

class voucher_industrial_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(voucher_industrial_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'amount_to_text': self._get_amount_to_text,
            'get_date_str_es': self._get_date_str_es,
            'get_lines_order': self._get_lines_order,
        })
    
    def _get_lines_order(self, moves, order_by='credit'):
        move_obj = self.pool.get('account.move.line')
        move_ids = [move.id for move in moves]
        move_ids = move_obj.search(self.cr, self.uid, (['id', 'in', move_ids],), order='credit desc', limit=None, count=False)
        moves = move_obj.browse(self.cr, self.uid, move_ids)
        return moves
    
    def _get_date_str_es(self, date_str):
        date_obj = time.strptime(date_str, '%Y-%m-%d')
        mes_int = int( time.strftime("%m", date_obj) )
        month_str = months_selection[mes_int-1][1]
        day = time.strftime('%d', date_obj)
        year = time.strftime('%Y', date_obj)
        date_str_str_es = "%s de %s del %s"%(day, month_str, year)
        return date_str_str_es
        
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
    
report_sxw.report_sxw('report.account.payment.voucher.industrial', 'account.voucher', 'addons/account_invoice_receipt/report/voucher_industrial_report.rml', parser=voucher_industrial_report, header=False)
