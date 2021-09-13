# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
# from odoo.addons.ehcs_qr_code_base.models.qr_code_base import generate_qr_code
import qrcode
import base64
from io import BytesIO


class PurchaseRequestInherit(models.Model):
    _inherit = "purchase.request"

    cmms_pr = fields.Boolean('CMMS PR')