# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo
#    All Rights Reserved.
############################################################################
#    Coded by: Fernando Irene Garcia (fernandoig1125@hotmail.com)
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

import time
from report import report_sxw
import locale

class report_saldos(report_sxw.rml_parse):

    def set_context(self, objects, data, ids, report_type=None):
        return super(report_saldos, self).set_context(objects, data, ids, report_type=report_type)
        
    def __init__(self, cr, uid, name, context):
        super(report_saldos, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_saldos_partners': self._get_saldos_partners,
            'formatLang2': self._formatLang2,
            'get_company': self._get_company,
            'get_address': self._get_address,
            'get_amounts_totales': self._get_amounts_totales,
        })
        
    def _formatLang2(self,value):
        locale.setlocale( locale.LC_ALL, '' )
        return locale.currency( value, grouping=True )
    
    def _get_company(self):
        user_obj = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner')
        partner_address_obj = self.pool.get('res.partner')
        self.company = user_obj.browse(self.cr, self.uid, [self.uid])[0]
        partner_id = self.company.company_id.partner_id.id
        address_id = partner_obj.address_get(self.cr, self.uid, partner_id, adr_pref=['default'])['default']
        self.address= partner_address_obj.browse(self.cr, self.uid, address_id)
        return self.company
        
    def _get_address(self):
        return self.address
        
    def _get_invoices(self, date_end = '', date_start = '', date_created = ''):
        if date_end == 0 and date_start == 0:
            return True
        elif date_end == 0 and date_start != 0:
            if time.strptime(date_created, '%Y-%m-%d %H:%M:%S') > time.strptime(date_start, '%Y-%m-%d %H:%M:%S'):
                return True
        elif date_end != 0 and date_start == 0:
            if time.strptime(date_created, '%Y-%m-%d %H:%M:%S') < time.strptime(date_end, '%Y-%m-%d %H:%M:%S'):
                return True
        elif date_end != 0 and date_start != 0:
            if time.strptime(date_created, '%Y-%m-%d %H:%M:%S') < time.strptime(date_end, '%Y-%m-%d %H:%M:%S') and time.strptime(date_created, '%Y-%m-%d %H:%M:%S') > time.strptime(date_start, '%Y-%m-%d %H:%M:%S'):
                return True
        return False
    
    def _get_amounts_totales(self, date_end, date_start, partner_ids):
        totales=[]
        amounts={}
        res = self._get_saldos_partners(date_end, date_start, partner_ids)
        amount_due_total=0
        amount_paid_total=0
        amount_receive_total=0
        amount_receive_total_total=0
        for r in res:
            amount_due_total+=r['amount_due']
            amount_paid_total+=r['amount_paid']
            amount_receive_total+=r['amount_receive']
            amount_receive_total_total+=r['amount_receive_total']
            currency_symbol = r['currency_symbol']
        amounts['amount_due_total']=amount_due_total
        amounts['amount_paid_total']=amount_paid_total
        amounts['amount_receive_total']=amount_receive_total
        amounts['amount_receive_total_total']=amount_receive_total_total
        amounts['currency_symbol']=currency_symbol or ''
        totales.append(amounts)
        return totales
        
    def _get_saldos_partners(self, date_end, date_start, partner_ids):
        result = []
        subscription_obj = self.pool.get('subscription.subscription')
        history_obj = self.pool.get('subscription.subscription.history')
        invoice_obj = self.pool.get('account.invoice')
        partner_obj = self.pool.get('res.partner')
        cron_obj = self.pool.get('ir.cron')
        for partner in partner_ids:
            subs_ids = subscription_obj.search(self.cr, self.uid, [('partner_id', '=', partner)])
            for subs in subs_ids:
                subscripcion = {}
                amount_paid = 0
                amount_due = 0
                amount_receive = 0
                values = subscription_obj.read(self.cr, self.uid, [subs], ['doc_lines', 'doc_source', 'state', 'name', 'date_init'])[0]
                registros_ids = values['doc_lines']
                doc_source = int(values['doc_source'].split(',')[1])
                amount_total_proforma = invoice_obj.read(self.cr, self.uid, [doc_source], ['amount_total'])[0]['amount_total']
                today = time.strftime('%Y-%m-%d %H:%M:%S')
                num_invoices = 0
                for registro in history_obj.browse(self.cr, self.uid, registros_ids):
                    date_created = registro.date
                    res = self._get_invoices(date_end, date_start, date_created)
                    if res == 1:
                        invoice_state = invoice_obj.read(self.cr, self.uid, [registro.document_id.id], ['state'])
                        if invoice_state:
                            amount_total = invoice_obj.read(self.cr, self.uid, [registro.document_id.id], ['amount_total'])
                            if invoice_state[0]['state'] == 'paid':
                                amount_paid += amount_total[0]['amount_total']
                                num_invoices += 1
                            else:
                                if invoice_state[0]['state'] == 'draft' or invoice_state[0]['state'] == 'open':
                                    date_create = history_obj.read(self.cr, self.uid, [registro.id], ['date'])[0]['date']
                                    if time.strptime(date_create, '%Y-%m-%d %H:%M:%S') < time.strptime(today, '%Y-%m-%d %H:%M:%S'):
                                        amount_due += amount_total[0]['amount_total']
                                    num_invoices += 1
                date_final = time.strftime('%Y-12-31 23:59:59')
                if time.strptime(date_end, '%Y-%m-%d %H:%M:%S') < time.strptime(date_final, '%Y-%m-%d %H:%M:%S') and time.strptime(date_end, '%Y-%m-%d %H:%M:%S') > time.strptime(today, '%Y-%m-%d %H:%M:%S'):
                    if values['state'] == 'done':
                        amount_expected = 0
                    else:
                        mes = int(date_end.split('-')[1])
                        amount_expected = amount_total_proforma*(mes-num_invoices)
                elif time.strptime(date_end, '%Y-%m-%d %H:%M:%S') < time.strptime(values['date_init'], '%Y-%m-%d %H:%M:%S') or time.strptime(date_end, '%Y-%m-%d %H:%M:%S') < time.strptime(today, '%Y-%m-%d %H:%M:%S') or values['state'] == 'done':
                    amount_expected = 0
                else:
                    subs_arg = '[[%s]]'%str(subs)
                    cron_id = cron_obj.search(self.cr, self.uid, [('args', '=', subs_arg), ('active', '=', True)])
                    if cron_id:
                        num_documentos = cron_obj.read(self.cr, self.uid, cron_id, ['numbercall'])[0]['numbercall']
                        amount_expected = amount_total_proforma*num_documentos
                subscripcion['amount_paid'] = amount_paid
                subscripcion['amount_due'] = amount_due
                subscripcion['amount_receive'] = amount_expected
                subscripcion['amount_receive_total'] = amount_expected+amount_due
                subscripcion['name'] = values['name']
                partner_name = partner_obj.browse(self.cr, self.uid, [partner])[0].name or ''
                partner_ref = partner_obj.browse(self.cr, self.uid, [partner])[0].ref or ''
                subscripcion['partner_name'] = partner_name
                subscripcion['partner_ref'] = partner_ref
                subscripcion['currency_symbol'] = subscription_obj.browse(self.cr, self.uid, subs_ids)[0].doc_source.currency_id.symbol or ''
                result.append(subscripcion)
        return result
        
report_sxw.report_sxw('report.report.saldos', 'account.invoice',
    'addons/report_balance/report/report_saldos.rml', parser=report_saldos, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
