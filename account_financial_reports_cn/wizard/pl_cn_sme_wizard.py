# -*- coding: utf-8 -*-
#    Copyright (c) Rooms For (Hong Kong) Limited T/A OSCG
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

from openerp.osv import fields, osv


class accounting_pl_cn_sme(osv.osv_memory):
    _name = "accounting.pl_cn_sme"
    _inherit = "account.common.report"
    _description = "PL Report for China SME"

    def onchange_country_id(self, cr, uid, ids, country_id=False, context=None):
        res = {}
        if country_id:
            partner_ids = self.pool.get('res.partner').search(cr, uid, [('country_id','=',country_id)], context=context)
            company_ids = self.pool.get('res.company').search(cr, uid, [('partner_id','in',partner_ids)], context=context)
            res['domain'] = {'chart_account_id': [('parent_id','=',False),('company_id','in',company_ids)]}
        return res

    _columns = {
        'country_id': fields.many2one('res.country', 'Country'),
        'account_report_id': fields.many2one('account.financial.report', 'Account Reports', required=True),
        'period_id': fields.many2one('account.period', 'Account Period')
    }

    def _get_country_id(self, cr, uid, context=None):
        model, res_id = self.pool['ir.model.data'].get_object_reference(cr, uid, 'base', 'cn')
        return res_id

    def _get_account_report(self, cr, uid, context=None):
        # TODO deprecate this it doesnt work in web
        menu_obj = self.pool.get('ir.ui.menu')
        report_obj = self.pool.get('account.financial.report')
        report_ids = []
        if context.get('active_id'):
            menu = menu_obj.browse(cr, uid, context.get('active_id')).name
            report_ids = report_obj.search(cr, uid, [('name','ilikepl',menu)])
        return report_ids and report_ids[0] or False

    _defaults = {
            'country_id': _get_country_id,
            'target_move': 'posted',
            'account_report_id': _get_account_report,
    }
    
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        used_context = super(accounting_pl_cn_sme, self).check_report(cr, uid, ids, context=context)['data']['form']['used_context']
        data = {}
        data['head'] = {}
        data['form'] = self.read(cr, uid, ids, ['account_report_id', 'fiscalyear_id', 'journal_ids', 'chart_account_id', 'period_id'], context=context)[0]
        for field in ['chart_account_id', 'account_report_id', 'fiscalyear_id', 'period_id']:
            if isinstance(data['form'][field], tuple):
                data['head'][field] = data['form'][field][1]
                data['form'][field] = data['form'][field][0]
        target_move = self.read(cr, uid, ids, ['target_move'])[0]['target_move']
        if target_move == 'posted':
            data['head']['target_move'] = 'All Posted Entries'
        elif target_move == 'all':
            data['head']['target_move'] = 'All Entries'
        if data['form']['period_id']:
            used_context['periods'] = [data['form']['period_id']]
        data['form']['used_context'] = used_context
        
        res = {
            'type': 'ir.actions.report.xml',
            'datas': data,
            'report_name': 'pl_cn_sme_report',
            }
        return res
    

    # this method is needed only to override the method in
    # account_common_report, or the system throws an error
    def _print_report(self, cr, uid, ids, data, context=None):
#         data['form'].update(self.read(cr, uid, ids, ['debit_credit', 'account_report_id', 'enable_filter', 'target_move'], context=context)[0])
        return self.pool['report'].get_action(cr, uid, [], 'account.report_financial', data=data, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: