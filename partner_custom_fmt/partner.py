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

from osv import osv
from osv import fields

class res_partner_visita(osv.osv):
    _name = 'res.partner.visita'
    _columns = {
        'name': fields.char('Nombre de Visita', size=64, required=True)
    }
res_partner_visita()

class res_partner_programa(osv.osv):
    _name = 'res.partner.programa'
    _columns = {
        'name': fields.char('Nombre de programa', size=64, required=True)
    }
res_partner_programa()

class res_partner_medio(osv.osv):
    _name = 'res.partner.medio'
    _columns = {
        'name': fields.char('Nombre de medio', size=64, required=True)
    }
res_partner_medio()

class res_partner_frecuencia(osv.osv):
    _name = 'res.partner.frecuencia'
    _columns = {
        'name': fields.char('Nombre de frecuencia', size=64, required=True)
    }
res_partner_frecuencia()

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns = {
        'partner_alumno_ids': fields.many2many('res.partner', 'res_partner_partner_rel', 'padrino_id', 'alumno_id', 'Alumnos'),
        'partner_padrino_ids': fields.many2many('res.partner', 'res_partner_partner_rel', 'alumno_id', 'padrino_id', 'Padrinos'),
        
        'visita_id': fields.many2one('res.partner.visita', "Fecha de visita"),
        'programa_id': fields.many2one('res.partner.programa', "Programa"),
        'medio_id': fields.many2one('res.partner.medio', "Medio"),
        'frecuencia_id': fields.many2one('res.partner.frecuencia', "Frecuencia"),
        #'fecha_visita': fields.char('Fecha de visita', size=68),
        #'programa': fields.char('Programa', size=68),
        #'medio': fields.char('Medio', size=68),
        #'frecuencia': fields.char('Frecuencia', size=68),
        
        'donativo': fields.float('Donativo'),
        'fecha_nacimiento': fields.date('Fecha de Nacimiento'),
        'padrino_ok': fields.boolean('Padrino'),
        #'is_padrino_add': fields.related('partner_id', 'padrino_ok', type='boolean', string='Padrino'),
    }
res_partner()
