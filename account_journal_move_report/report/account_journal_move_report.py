# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    Info (info@vauxoo.com)
############################################################################
#    Coded by: isaac (isaac@vauxoo.com)
#    Coded by: moylop260 (moylop260@vauxoo.com)
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
import time
import pooler
from dateutil.relativedelta import relativedelta
import datetime


class account_journal_move_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_journal_move_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_objects': self._get_objects,
            'get_journal': self._get_journal,
            'get_balance': self._get_balance,
            'set_objects': self._set_objects,
            'get_account': self._get_account,
            'get_address': self._get_address,
            'get_periods': self._get_periods,
            'get_period_start': self._get_period_start,
            'get_period_end': self._get_period_end,
        })

    def _get_account(self):
        return self.account

    def _get_objects(self):
        return self.objects

    def _set_objects(self, journal_id, date_start, date_end, filter_type, period_start, period_end):
        move_line_obj = self.pool.get('account.move.line')
        journal_obj = self.pool.get('account.journal')
        partner_obj = self.pool.get('res.partner')
        partner_address_obj = self.pool.get('res.partner')
        account_period_obj = self.pool.get('account.period')

        self.journal = journal_obj.browse(self.cr, self.uid, [journal_id[0]])[0]
        self.account = self.journal.default_debit_account_id# and self.journal.default_debit_account_id.id or False
        account_id = self.account and self.account.id or False
        self.period_start_id = account_period_obj.browse(self.cr, self.uid, [period_start[0]])[0]
        self.period_end_id = account_period_obj.browse(self.cr, self.uid, [period_end[0]])[0]

        filters_gral = [('account_id', '=', account_id),]
        filters1 = list( filters_gral )
        filters2 = list( filters_gral )
        date_start_obj=time.strptime(date_start,'%Y-%m-%d')

        #------------------------------------------------------------------------Por fecha
        if filter_type == 'date':
            filters1.extend( [
                ('date','>=', date_start),
                ('date','<=', date_end),
            ])
            filters2.extend( [
            ('date', '>=',  time.strftime('%Y-01-01',date_start_obj)),#Cambiar al anio de la fecha que se esta sacando el reporte
            ('date', '<', date_start),
            ])
            self.filter_type=True

        #------------------------------------------------------------------------Por Perido
        elif filter_type == 'period':
            subq="""select * from account_period
                    where date_start>= (select date_start from account_period ini where ini.id=%s)
                        and date_stop <= (select date_stop from account_period fin where fin.id=%s)
            """%( period_start[0], period_end[0])
            self.cr.execute( subq )
            period_ids_rang = [ period_id[0] for period_id in self.cr.fetchall() ]
            filters1.extend( [
                ('period_id','in', period_ids_rang),
            ])

            subquery = """SELECT period_past.id
                    FROM account_period period_past
                    INNER JOIN
                      (
                        SELECT *
                        FROM account_period
                        WHERE id = %s
                      ) period_current
                    ON -- period_current.fiscalyear_id = period_past.fiscalyear_id
                     --AND
                     period_current.date_start > period_past.date_start
                     AND period_current.date_stop > period_past.date_stop
                """%( period_start[0] )
            self.cr.execute( subquery )
            period_ids = [ period_id[0] for period_id in self.cr.fetchall() ]
            filters2.extend( [
                ('period_id','in', period_ids),
            ])
            self.filter_type=False

        move_line_ids = move_line_obj.search(self.cr, self.uid, filters1, order='date asc, ref asc')
        move_lines = move_line_obj.browse(self.cr, self.uid, move_line_ids)
        lines_posted =[]
        for move_lines_posted in move_lines:
            if move_lines_posted.move_id.state == 'posted':
                lines_posted.append(move_lines_posted)
        self.objects = lines_posted
        #Inicia proceso de saldo inicial

        move_line_ids2 = move_line_obj.search(self.cr, self.uid, filters2, order='date asc, ref asc')
        move_lines2 = move_line_obj.browse(self.cr, self.uid, move_line_ids2)
        self.balance_initial = 0
        for move_line2 in move_lines2:
            
            anio_move_line = move_line2.period_id.fiscalyear_id.id
            anio_period = self.period_start_id.fiscalyear_id.id
            
            if anio_move_line <> anio_period:
                #Se obtienen los ids de los años fiscales, esto para que en cambio de año fiscal, valide el diario para que no duplique el saldo inicial de la poliza de apertura del periodo anterior.
                if move_line2.move_id.state == 'posted' and move_lines_posted.journal_id==journal_id:
                    self.balance_initial += move_line2.debit-move_line2.credit
            else:
                if move_line2.move_id.state == 'posted':
                    self.balance_initial += move_line2.debit-move_line2.credit
                    
        #Termina proceso de saldo inicial

        partner_id = self.journal.company_id.partner_id.id
        address_id = partner_obj.address_get(self.cr, self.uid, [partner_id], adr_pref=['default'])['default']
        self.address= partner_address_obj.browse(self.cr, self.uid, address_id)
        return ''

    def _get_periods (self):
        return self.filter_type

    def _get_period_start (self):
        return self.period_start_id.name

    def _get_period_end (self):
        return self.period_end_id.name

    def _get_balance(self, num=0):
        self.balance_initial += num
        return self.balance_initial

    def _get_journal(self):
        return self.journal

    def _get_address(self):
        return self.address

report_sxw.report_sxw('report.account.journal.move.report', 'account.move.line','addons/account_journal_move_report/report/account_journal_move_report.rml', parser=account_journal_move_report)
