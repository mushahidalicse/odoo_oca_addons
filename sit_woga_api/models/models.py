from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, AccessError, ValidationError
import odoo.addons.decimal_precision as dp
import datetime

# class PurchaseRequestLineInherit(models.Model):
#     _inherit = "purchase.request.line"

#     cmms_pr = fields.Boolean('CMMS Request', related='request_id.cmms_pr',)
#     cmms_modelnum = fields.Char("CMMS MODEL NUM")
#     cmms_polinenum = fields.Char("CMMS PO LINE NUM")
