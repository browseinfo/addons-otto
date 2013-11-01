# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    Info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Fernando Irene Garcia (fernando@vauxoo.com)
#              Isaac Lopez (isaac@vauxoo.com)
#              Luis Torres (luis_t@vauxoo.com)
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
from datetime import datetime
from operator import itemgetter

class report_saldos_detalle(report_sxw.rml_parse):

    def set_context(self, objects, data, ids, report_type=None):
        return super(report_saldos_detalle, self).set_context(objects, data, ids, report_type=report_type)
        
    def __init__(self, cr, uid, name, context):
        super(report_saldos_detalle, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_saldos_partners': self._get_saldos_partners,
            'formatLang2': self._formatLang2,
            'get_company': self._get_company,
            'get_address': self._get_address,
            'get_amounts_totales': self._get_amounts_totales,
            'datetime2date': self._datetime2date,
            'get_period_amount':self._get_period_amount,
            'get_amount_received':self._get_amount_received,
            'get_payment_amount':self._get_payment_amount,
            'get_dif_to_load':self._get_dif_to_load,
            'get_symbol_amount_received':self._get_symbol_amount_received,
            'get_symbol_payment_amount':self._get_symbol_payment_amount,
            'get_symbol_period_amount':self._get_symbol_period_amount,
        })
        
    def _datetime2date(self, date2):
        try:
            if datetime.strptime( date2, '%Y-%m-%d %H:%M:%S'):
                format_date = datetime.strptime( date2, '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
                return format_date
        except:
            pass
        try:
            if datetime.strptime( date2, '%Y-%m-%d'):
                #~ print '*********dentro del formato ymd se convierte a dmy format_date:',date2
                format_date = datetime.strptime( date2, '%Y-%m-%d').strftime('%d-%m-%Y')
                return format_date
        except:
            pass
        try:
            if datetime.strptime( date2, '%m-%d-%Y'):
                format_date = datetime.strptime( date2, '%m-%d-%Y').strftime('%d-%m-%Y')
                return format_date
        except:
            pass
        
        return date2
            
    def _formatLang2(self,value):
        locale.setlocale( locale.LC_ALL, '' )
        return locale.currency( value, grouping=True )
    
    def _get_company(self):
        user_obj = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner')
        partner_address_obj = self.pool.get('res.partner')
        self.company = user_obj.browse(self.cr, self.uid, [self.uid])[0]
        partner_id = self.company.company_id.partner_id.id
        address_id = partner_obj.address_get(self.cr, self.uid, [partner_id], adr_pref=['default'])['default']
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
    
    def _get_amounts_totales(self, date_end, date_start, partner_id):
        result = []
        totales = {}
        symbol = ''
        amount_paid = 0
        amount_cargo = 0
        amount_saldo = 0
        partner_ids = []
        partner_ids.append(partner_id)
        res = self._get_saldos_partners(date_end, date_start, partner_ids)
        for r in res:
            if r['invoices']:
                for invoice in r['invoices']:
                    amount_paid += invoice['amount_paid']
                    amount_cargo += invoice['amount_cargo']
                    amount_saldo += invoice['amount_saldo']
                    symbol = invoice['symbol']
            else:
                amount_paid = 0
                amount_cargo = 0
                amount_saldo = 0
            totales['amount_paid'] = amount_paid
            totales['amount_cargo'] = amount_cargo
            totales['amount_saldo'] = amount_saldo
            totales['symbol'] = symbol
            result.append(totales)
        return result
        
    def _get_saldos_partners(self, date_end, date_start, partner_ids):
        result = []
        subscription_obj = self.pool.get('subscription.subscription')
        history_obj = self.pool.get('subscription.subscription.history')
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        voucher_obj = self.pool.get('account.voucher')
        voucher_line_obj = self.pool.get('account.voucher.line')
        partner_obj = self.pool.get('res.partner')
        cron_obj = self.pool.get('ir.cron')
        self.totales={}
        for partner in partner_ids:
            subs_ids = subscription_obj.search(self.cr, self.uid, [('partner_id', '=', partner)])
            partner_invoices = []
            partner_documents = []
            data_report = []
            subscripcion = {}
            invoice_ids = invoice_obj.search(self.cr, self.uid, [('partner_id', '=', partner), ('date_invoice','>=', datetime.strptime( date_start, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')),('date_invoice','<=', datetime.strptime( date_end, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')), ('state','<>', 'draft'),('state','<>', 'proforma2')])
            invoice_values = invoice_obj.browse(self.cr, self.uid, invoice_ids)
            #~ num_invoices = 0
            #-------------------------------------------------------
            self.amount_doc_period=0
            self.amount_received=0
            self.payment_amount=0
            self.symbol_payment_amount=''
            self.symbol_amount_doc_period=''
            self.symbol_received=''
            for subs in subs_ids:
                docs_created=history_obj.search(self.cr, self.uid, [('subscription_id', '=', subs),('date','>=', date_start),('date','<=', date_end)])
                prof_id=subscription_obj.search(self.cr, self.uid, [('id', '=', subs)])
                prof = subscription_obj.browse(self.cr, self.uid, prof_id)[0].doc_source.id
                for id_doc in docs_created:
                    documents = {}
                    history_id = history_obj.browse(self.cr, self.uid, id_doc).document_id.id
                    date_doc=history_obj.browse(self.cr, self.uid, id_doc).date
                    valor_doc=invoice_obj.browse(self.cr, self.uid, prof).amount_total
                    currency_doc=invoice_obj.browse(self.cr, self.uid, prof).currency_id.symbol
                    inv_line_ids = invoice_line_obj.search(self.cr, self.uid, [('invoice_id', '=', history_id )],limit=1)
                    conc_doc = invoice_line_obj.browse(self.cr, self.uid, inv_line_ids) and invoice_line_obj.browse(self.cr, self.uid, inv_line_ids)[0].name or ''
                    documents['date_doc'] = date_doc or False
                    documents['valor_doc'] = valor_doc or False
                    documents['conc_doc'] = conc_doc or False
                    documents['currency_doc'] = currency_doc or False
                    partner_documents.append(documents)
                    self.amount_doc_period = self.amount_doc_period + valor_doc
                    self.symbol_amount_doc_period = currency_doc
            for inv in invoice_values:
                invoice = {}
                amount_paid = 0
                monto_pago = 0
                amount_cargo = 0
                amount_saldo = 0
                date_invoice = ''
                type_pago = ''
                concepto = ''
                no_boleta = ''
                no_recibo = ''
                serie = ''
                fecha_pago=''
                if inv.state == 'paid':
                    voucher_line = voucher_line_obj.search(self.cr, self.uid, [('name', '=', inv.number)])
                    if voucher_line:
                        voucher_line_values = voucher_line_obj.browse(self.cr, self.uid, voucher_line)[0]
                        type_pago = voucher_line_values.voucher_id.journal_id.name
                        no_boleta = voucher_line_values.voucher_id.reference
                        fecha_pago = voucher_line_values.voucher_id.date
                        monto_pago = voucher_line_values.voucher_id.amount
                date_invoice = datetime.strptime( inv.date_invoice, '%Y-%m-%d').strftime('%m-%d-%Y') or ''
                if inv.number:
                    for l in inv.number:
                        if l not in '0123456789':
                            serie += l
                        if l in '0123456789':
                            no_recibo += l
                
                invoice['monto_recibo'] = inv.amount_total or False
                invoice['forma_pago'] = type_pago
                invoice['fecha_pago'] = fecha_pago or False
                invoice['amount_paid'] = monto_pago or False
                invoice['amount_cargo'] = amount_cargo
                invoice['date_invoice'] = date_invoice
                invoice['type_pago'] = type_pago
                invoice['no_boleta'] = no_boleta
                invoice['concepto'] = concepto
                invoice['serie'] = serie
                invoice['no_recibo'] = no_recibo
                invoice['amount_saldo'] = amount_saldo
                invoice['symbol'] = inv.currency_id.symbol
                ids_invo=invoice_line_obj.search(self.cr, self.uid, [('invoice_id','=',inv.id)])
                a=0
                for id_inv in ids_invo:
                    concep_inv=invoice_line_obj.browse(self.cr, self.uid,id_inv).product_id.name_template
                    if concep_inv == 'Donaciones In' or inv.state == 'cancel':
                        a=1
                        
                if a==0:
                    partner_invoices.append(invoice)
                    self.amount_received = self.amount_received + inv.amount_total
                    self.payment_amount = self.payment_amount + monto_pago
                    self.symbol_received=inv.currency_id.symbol
                    self.symbol_payment_amount=inv.currency_id.symbol
            invoices_list=partner_invoices[:]
            cont=0
            cant_inv=len(invoices_list)
            cant_doc=len(partner_documents)
            if cant_doc > cant_inv:
                for dic in partner_documents:
                    if cant_doc > cant_inv:
                        invoices_list.append({})
                        cant_inv=cant_inv+1
            for invo in invoices_list:
                if cant_doc > cont:
                    invo['izq']=partner_documents[cont]
                    cont=cont+1
                data_report.append(invo)
                
            partner_values = partner_obj.browse(self.cr, self.uid, [partner])[0]
            subscripcion['partner_name'] = partner_values.name
            subscripcion['partner_id'] = partner_values.id
            subscripcion['invoices'] =  partner_invoices
            subscripcion['partner_program'] = partner_values.programa_id.name
            subscripcion['partner_ref'] = partner_values.ref              
            subscripcion['data_report'] = data_report
            result.append(subscripcion)
            result_ordenado = []
            self.totales[partner_values.name] = {'total_period': self.amount_doc_period,'symbol_total_period':self.symbol_amount_doc_period, 'total_pagado': self.payment_amount,'symbol_total_pagado':self.symbol_received,'total_facturado':self.amount_received,'symbol_total_facturado':self.symbol_payment_amount}
        return result
        
    def _get_period_amount(self,partner):
        for part in self.totales:
            if part == partner:
                return self.totales[part]['total_period']
        return False
        
    def _get_symbol_period_amount(self,partner):
        for part in self.totales:
            if part==partner:
                return self.totales[part]['symbol_total_period']
        return False
        
    def _get_amount_received(self,partner):
        for part in self.totales:
            if part == partner:
                return self.totales[part]['total_facturado']
        return False
        
    def _get_symbol_amount_received(self,partner):
        for part in self.totales:
            if part==partner:
                return self.totales[part]['symbol_total_pagado']
        return False
        
    def _get_payment_amount(self,partner):
        for part in self.totales:
            if part == partner:
                return self.totales[part]['total_pagado']
        return False
        
    def _get_symbol_payment_amount(self,partner):
        for part in self.totales:
            if part==partner:
                return self.totales[part]['symbol_total_facturado']
        return False
                
    def _get_dif_to_load(self,partner):
        dif = self._get_period_amount(partner) -  self._get_amount_received(partner)
        return dif
        
        
report_sxw.report_sxw('report.report.saldos.detalle', 'account.invoice',
    'addons/report_balance/report/report_saldos_detalle.rml', parser=report_saldos_detalle, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
