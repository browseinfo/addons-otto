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
{
    "name" : " Wizard Reporte de Saldos ",
    "version" : "0.1",
    "author" : "Vauxoo",
    "category" : "Localization/Mexico",
    "license" : "AGPL-3",
    "description": """ Genera un reporte de saldos conforme a un registro periodico generado. """,
    "depends" : ["base", "account_voucher", "partner_custom_fmt", "subscription"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : ['wizard/report_saldos_view.xml', 'report_saldos.xml'],
    "active": False,
    "test":[],
    "installable": True,
}