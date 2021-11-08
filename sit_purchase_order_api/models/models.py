from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, AccessError, ValidationError
import odoo.addons.decimal_precision as dp
import datetime

class PurchaseRequestInherit(models.Model):
    _inherit = "purchase.request"

    cmms_pr = fields.Boolean('CMMS Request')
    cmms_name = fields.Char('CMMS Reference', track_visibility='onchange')
    cmms_billto = fields.Char('BILLTO')
    cmms_shipto = fields.Char('SHIPTO')
    cmms_e1edk01_belnr = fields.Char('E1EDK01_BELNR')
    cmms_e1edk14_006 = fields.Char('E1EDK14_006')
    cmms_e1edk14_007 = fields.Char('E1EDK14_007')
    cmms_e1edk14_008 = fields.Char('E1EDK14_008')
    cmms_e1edk14_012 = fields.Char('E1EDK14_012')
    cmms_e1edk14_016 = fields.Char('E1EDK14_016')
    cmms_e1edka1_partwb = fields.Char('E1EDKA1_PARTWB')
    cmms_e1edka1_parvws = fields.Char('E1EDKA1_PARVWS')
    cmms_e1edp01_action = fields.Char('E1EDP01_ACTION')
    cmms_e1edp01_pstyv = fields.Char('E1EDP01_PSTYV')
    cmms_revisionnum = fields.Char('REVISIONNUM')

    @api.model
    def create(self, vals):
        if vals.get('cmms_pr'):
            vals['cmms_name'] = self.env['ir.sequence'].next_by_code('purchase_request_cmms') or _('New')
            # self.action_send_pr_cmms_email('ctannous@rsa-metro.com')
        request = super(PurchaseRequestInherit, self).create(vals)
        template = self.env.ref('sit_purchase_order_api.email_template_purchase_request_cmms_create')
        template.send_mail(request.id, force_send=True)
        return request

class PurchaseRequestLineInherit(models.Model):
    _inherit = "purchase.request.line"

    cmms_pr = fields.Boolean('CMMS Request', related='request_id.cmms_pr',)
    cmms_modelnum = fields.Char("CMMS MODEL NUM")
    cmms_polinenum = fields.Char("CMMS PO LINE NUM")
