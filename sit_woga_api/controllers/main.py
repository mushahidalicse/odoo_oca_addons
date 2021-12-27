# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import logging
import werkzeug

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.web_settings_dashboard.controllers.main import WebSettingsDashboard as Dashboard
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

class WogaController(http.Controller):

    @http.route(['/get_supplier_by_id'], methods=['POST'], type='json', auth="user")
    def get_vendor_by_id(self,**rec):
        if request.jsonrequest:
            if rec['id']:
                vendor = request.env['res.partner'].search([('id','=',rec['id'])],limit=1)
                product_ids = request.env['product.supplierinfo'].search([('name','=',vendor.id)],limit=10)
                vendor_products = request.env['product.template'].search([('id','in',product_ids.ids)])
                products = []
                if vendor_products:
                    for prod in vendor_products:
                        image_url = request.env['ir.config_parameter'].get_param('web.base.url')
                        image_url += '/web/image?model=product.template&field=image_medium&id='+str(prod.id)
                        product = {
                            'id':prod.id,
                            'name':prod.name,
                            'list_price':prod.list_price,
                            'cost_price':prod.standard_price,
                            'product_image':image_url
                        }
                        products.append(product)
                vend = []
                for rec in vendor:
                    vend = {
                        'id':rec.id,
                        'name':rec.name,
                        'vendor_name':rec.name,
                        'address':rec.street,
                        'vat':rec.vat,
                        'phone':rec.phone,
                        'mobile':rec.mobile,
                        'email':rec.email,
                        'language':rec.lang,
                        'supplier':rec.supplier,
                        'products':products
                    }
                data = {"status":200,"response":vend,"message":"success"}
                return data

    @http.route(['/get_suppliers'], methods=['POST'], type='json', auth="user")
    def get_vendors(self):
        vendors = request.env['res.partner'].search([('supplier','=',True)],limit=10)
        vend = []
        for rec in vendors:
            vals = {
                'id':rec.id,
                'name':rec.name,
                'vendor_name':rec.name,
                'address':rec.street,
                'vat':rec.vat,
                'phone':rec.phone,
                'mobile':rec.mobile,
                'email':rec.email,
                'language':rec.lang,
                'supplier':rec.supplier
            }
            vend.append(vals)
        data = {"status":200,"response":vend,"message":"success"}
        return data

    @http.route(['/get_products'], methods=['POST'], type='json', auth="user")
    def get_products(self):
        products = request.env['product.template'].search([],limit=10)
        prod = []
        for rec in products:
            sellers = []
            for sel in rec.seller_ids:
                seller = {
                    'id':sel.name.id,
                    'name':sel.name.name,
                    'minimum_qty':sel.min_qty,
                    'price':sel.price
                }
                sellers.append(seller)
            vals = {
                'id':rec.id,
                'name':rec.name,
                'can_be_sale':rec.sale_ok,
                'can_be_purchase':rec.purchase_ok,
                'product_type':rec.type,
                'default_code':rec.default_code,
                'barcode':rec.barcode,
                'categ_id':rec.categ_id,
                'alternative_name':rec.alternative_name,
                'old_barcode':rec.old_barcode,
                'sale_price':rec.lst_price,
                'cost_price':rec.standard_price,
                'uom':rec.uom_id,
                'uom_po':rec.uom_po_id,
                'sellers':sellers,
            }
            prod.append(vals)
        data = {"status":200,"response":prod,"message":"success"}
        return data
    
    @http.route('/web/forgot_password', methods=['POST'], type='json', auth='public', website=True, sitemap=False)
    def web_auth_forgot_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if 'error' not in qcontext:
            try:
                login = qcontext.get('login')
                assert login, _("No login provided.")
                _logger.info(
                    "Password reset attempt for <%s> by user <%s> from %s",
                    login, request.env.user.login, request.httprequest.remote_addr)
                request.env['res.users'].sudo().reset_password(login)
                qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        # response = request.render('auth_signup.reset_password', qcontext)
        # response.headers['X-Frame-Options'] = 'DENY'
        return qcontext

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""

        get_param = request.env['ir.config_parameter'].sudo().get_param
        return {
            'signup_enabled': request.env['res.users']._get_signup_invitation_scope() == 'b2c',
            'reset_password_enabled': get_param('auth_signup.reset_password') == 'True',
        }

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = request.params.copy()
        qcontext.update(self.get_auth_signup_config())
        return qcontext


    @http.route(['/web/sign_up'], methods=['POST'], type='json', auth="public")
    def sign_up_public_user(self,**rec):
        users = request.env['res.users'].sudo().search([],limit=1)
        var = {
            "id":users.id,
            "grp":users.groups_id
        }
        return var
