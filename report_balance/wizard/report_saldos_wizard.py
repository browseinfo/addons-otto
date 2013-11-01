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

from osv import osv, fields
from tools.translate import _

class wizard_report_saldos(osv.osv_memory):
    _name = 'wizard.report.saldos'

    _columns = {
          'partner_ids': fields.many2many('res.partner','report_saldos_rel','partner_id','report_id','Partners'),
          'date_start':fields.datetime('Fecha Inicio'),
          'date_end':fields.datetime('Fecha Fin'),
          'type_report':fields.selection([('general', 'General'),('detalle', 'Detalle')], 'Tipo de Reporte'),
          'notice':fields.text('Leyenda')
    }
     
    _defaults = {
        'date_start':lambda*a:time.strftime('%Y-01-01 00:00:00'),
        'date_end':lambda*a:time.strftime('%Y-12-31 23:59:59'),
        'type_report': 'detalle',
    }
    
    def create_report(self, cr, uid, ids, context=None):
        report_name = ''
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        datas['model'] = 'account.invoice'
        datas['form'] = self.read(cr, uid, ids)[0]
        type = datas['form']['type_report']
        if type == 'detalle':
            report_name = 'report.saldos.detalle'
        else:
            report_name = 'report.saldos'
        return {
            'type': 'ir.actions.report.xml',
            'report_name': report_name,
            'datas': datas,
        }
wizard_report_saldos()
