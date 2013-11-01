# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    Info (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: isaac (isaac@vauxoo.com)
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

from osv import osv
from osv import fields

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _order = "internal_number"
    def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        res = super(account_invoice,self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
        partner_obj = self.pool.get('res.partner')
        if partner_id:
            partner_brw = partner_obj.browse(cr, uid, partner_id)

        res['value']['visita_id'] = partner_id and partner_brw.visita_id.id or False
        res['value']['programa_id'] = partner_id and partner_brw.programa_id.id or False
        res['value']['medio_id'] = partner_id and partner_brw.medio_id.id or False
        res['value']['frecuencia_id'] = partner_id and partner_brw.frecuencia_id.id or False
        return res

    _columns = {
        'visita_id': fields.many2one('res.partner.visita', "Fecha de visita"),
        'programa_id': fields.many2one('res.partner.programa', "Programa"),
        'medio_id': fields.many2one('res.partner.medio', "Medio"),
        'frecuencia_id': fields.many2one('res.partner.frecuencia', "Frecuencia"),
    }
account_invoice()
