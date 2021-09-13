# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
# from odoo import fields as odoo_fields, tools, _
from odoo.exceptions import ValidationError, AccessError, MissingError, UserError
from odoo.http import Controller, request, route
from odoo import fields, http, tools, _


class PurchaseController(http.Controller):

    @http.route(['/get_purchase_orders'], type='json', auth="user")
    def get_purchase_orders(self):
        po = request.env['purchase.order'].search([])
        pos = []
        for rec in po:
            lines = []
            for ol in rec.order_line:
                line = {
                    'product':ol.product_id.name,
                    'description':ol.name,
                    'date':ol.date_planned,
                    'quantity':ol.product_qty,
                    'uom':ol.product_uom.name,
                    'unit_price':ol.price_unit,
                    'price':ol.price_subtotal,
                }
                lines.append(line)
            vals = {
                'id':rec.id,
                'name':rec.name,
                'vendor_name':rec.partner_id.name,
                'vendor_ref':rec.partner_ref,
                # 'currency':rec.currency_id.name,
                'order_date':rec.date_order,
                'source':rec.origin,
                # 'company':rec.company_id.name,
                'price_before_disc':rec.amount_untaxed,
                'tax':rec.amount_tax,
                'total_amount':rec.amount_total,
                'lines':lines,
            }

            pos.append(vals)
        data = {"status":200,"response":pos,"message":"success"}
        return data


    @http.route(['/get_vendors'], type='json', auth="user")
    def get_vendors(self):
        vendors = request.env['res.partner'].search([])
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


    @http.route(['/create_vendor'], type='json', auth="user")
    def create_vendor(self, **rec):
        if request.jsonrequest:
            print("aaaaaaaaaaaaaaaaaaaaaaaaaa",rec)
            if rec['name']:
                name = rec['name']
                vendor = request.env['res.partner'].sudo().search([('name','like',str(name))],limit=1)
                res = []
                if not vendor: 
                    vals={
                        "name":rec["name"],
                    }
                    vals['street'] = rec['address']
                    vals['vat']=int(rec['vat'])
                    vals['phone']=rec['phone']
                    vals['supplier']=rec['supplier']
                    vendor = request.env['res.partner'].sudo().create(vals)
                resp = {
                    "id":vendor.id,
                    "name":vendor.name,
                }
                res.append(resp)
                data = {"status":200,"response":res,"message":"success"}
                return data

    @http.route(['/create_purchase_orders'], type='json', auth="user")
    def create_purchase_order(self, **rec):
        if request.jsonrequest:
            res = []

            if "id" in rec:
                po_id = rec['id']
                po = request.env['purchase.order'].sudo().search([('id','=',int(po_id))],limit=1)

            if "partner_id" in rec:
                partner = request.env['res.partner'].sudo().search([('id','=',int(rec['partner_id']))],limit=1)

            if "partner_name" in rec:
                partner = request.env['res.partner'].sudo().search([('name','ilike',rec['partner_name'])],limit=1)

            if not "partner_id" in rec and not "partner_name" in rec:
                print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

            else: 
                vals = {
                    'partner_id':int(rec['partner_id'])
                }
                # vals['company_id']=int(rec['company_id'])
                po = request.env['purchase.order'].sudo().create(vals)

            resp = {
                "id":po.id,
                "name":po.name,
                "partner_name":po.partner_id.name,
                "currency_id":po.currency_id.name,
                "company_id":po.company_id.name,
                "order_date":po.date_order
            }
            res.append(resp)
            data = {"status":200,"response":res,"message":"success"}
            return data

    @http.route(['/get_products'], type='json', auth="user")
    def get_products(self):
        products = request.env['product.template'].search([])
        prod = []
        for rec in products:
            sellers = []
            for sel in rec.seller_ids:
                seller = {
                    'name':sel.name,
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
    
    @http.route(['/get_purchase_requests'], type='json', auth="public")
    def get_purchase_request(self):
        pr = request.env['purchase.request'].search([('cmms_pr','=',True)])
        prs = []
        
        if pr:
            for rec in pr:
                lines = []
                for ol in rec.line_ids:
                    line = {
                        'product':ol.product_id.name,
                        'description':ol.name,
                        'quantity':ol.product_qty,
                        'uom':ol.product_uom_id.name,
                        'requested_date':ol.date_required,
                    }
                    lines.append(line)
                vals = {
                    'rekeep_pr_id':rec.id,
                    'pr_name':rec.name,
                    'creation_date':rec.date_start,
                    'source':rec.origin,
                    'description':rec.description,
                    'lines':lines,
                }

                prs.append(vals)
            data = {"status":200,"response":prs,"Message":"All CMMS Purchase Request"}
        else:
            data = {"status":404,"response":"","Error":"There is no any CMMS purchase requests available in rekeep database."}        
        return data

    @http.route(['/create_purchase_request'], auth="user", type='json')
    def create_purchase_request(self, **rec):
        if request.jsonrequest:
            res = []
            vals = {
                'requested_by': request.env.user.id,
                'date_start': fields.Date.today(),
                'picking_type_id': 6,
                'cmms_pr':True,
                'assigned_to':2,
            }

            if "Description" in rec:
                vals['description'] = rec['Description']

            if "SourceDocument" in rec:
                vals['origin'] = rec['SourceDocument']
            else:
                data = {"status":200,"response":"Please add cmms source document reference","message":"success"}
                return data
            
            if "Lines" in rec:
                lines = []
                for line in rec['Lines']:
                    if not "ProductQuantity" in line:
                        data = {"status":404,"response":"Please add product quantities","message":"Error"}
                        return data

                    if "ProductID" in line:
                        product = request.env['product.product'].search([('id','=',int(line['ProductID']))],limit=1)
                    
                    if "ProductName" in line:
                        product = request.env['product.product'].search([('name','like',str(line['ProductName']))],limit=1)

                    if "ProductName" in line and "ProductID" in line:
                        product = request.env['product.product'].search([('id','=',int(line['ProductID'])),('name','like',str(line['ProductName']))],limit=1)

                    if product:
                        line = {
                            'product_id':product.id,
                            'name':product.name,
                            'product_qty':line['ProductQuantity'],
                            'product_uom_id':product.uom_id.id,
                            'date_required':fields.Date.today(),
                        }
                        lines.append((0, 0, line))
                    else:
                        data = {"status":404,"response":"Product Not Found","message":"Error"}
                        return data

                vals['line_ids'] = lines
            else:
                data = {"status":204,"response":"Please add product lines","message":"Error"}
                return data

            pr = request.env['purchase.request'].sudo().create(vals)
            pr.submit_purchase_request()
            rsp_lines = []
            for prl in pr.line_ids:
                rsp_line = {
                    "ProductID":prl.product_id.id,
                    "ProductName":prl.product_id.name,
                    "ProductUOM":prl.product_uom_id.id,
                    "ProductQuantity":prl.product_qty,
                    "Description":prl.name,
                    "Date":prl.date_required,
                }
                rsp_lines.append(rsp_line)


            resp = {
                "PurchaseRequest":pr.id,
                "PurchaseRequestName":pr.name,
                "SourceDocument":pr.origin,
                "Description":pr.description,
                "CreateDate":pr.date_start,
                "Lines":rsp_lines
            }
            res.append(resp)
            data = {"status":200,"response":res,"Message":"Purchase Request Created!"}
            return data

    @http.route(['/create_purchase_request_new'], methods=['POST'], csrf=False, auth="user", type='json')
    def create_purchase_request(self, **post):
        if request.jsonrequest:
            res = []
            vals = {
                'requested_by': request.env.user.id,
                'date_start': fields.Date.today(),
                'picking_type_id': 6,
                'cmms_pr':True,
                'assigned_to':2,
            }
            
            if "Description" in post:
                vals['description'] = post.get('Description')

            if "SourceDocument" in post:
                vals['origin'] = post.get('SourceDocument')
            else:
                data = {"status":200,"response":"Please add cmms source document reference","message":"success"}
                return data
            
            if "Lines" in post:
                lines = []
                for line in post.get('Lines'):
                    if not "ProductQuantity" in line:
                        data = {"status":404,"response":"Please add product quantities","message":"Error"}
                        return data

                    if "ProductID" in line:
                        product = request.env['product.product'].search([('id','=',int(line['ProductID']))],limit=1)
                    
                    if "ProductName" in line:
                        product = request.env['product.product'].search([('name','like',str(line['ProductName']))],limit=1)

                    if "ProductName" in line and "ProductID" in line:
                        product = request.env['product.product'].search([('id','=',int(line['ProductID'])),('name','like',str(line['ProductName']))],limit=1)

                    if product:
                        line = {
                            'product_id':product.id,
                            'name':product.name,
                            'product_qty':line['ProductQuantity'],
                            'product_uom_id':product.uom_id.id,
                            'date_required':fields.Date.today(),
                        }
                        lines.append((0, 0, line))
                    else:
                        data = {"status":404,"response":"Product Not Found","message":"Error"}
                        return data

                vals['line_ids'] = lines
            else:
                data = {"status":204,"response":"Please add product lines","message":"Error"}
                return data

            pr = request.env['purchase.request'].sudo().create(vals)
            pr.submit_purchase_request()
            rsp_lines = []
            for prl in pr.line_ids:
                rsp_line = {
                    "ProductID":prl.product_id.id,
                    "ProductName":prl.product_id.name,
                    "ProductUOM":prl.product_uom_id.id,
                    "ProductQuantity":prl.product_qty,
                    "Description":prl.name,
                    "Date":prl.date_required,
                }
                rsp_lines.append(rsp_line)


            resp = {
                "PurchaseRequest":pr.id,
                "PurchaseRequestName":pr.name,
                "SourceDocument":pr.origin,
                "Description":pr.description,
                "CreateDate":pr.date_start,
                "Lines":rsp_lines
            }
            res.append(resp)
            data = {"status":200,"response":res,"Message":"Purchase Request Created!"}
            return data