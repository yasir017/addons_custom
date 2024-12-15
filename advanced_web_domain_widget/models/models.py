from odoo import api, fields, models, tools, _


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs):
        res = super().search_read(domain, fields, offset, limit, order, **read_kwargs)
        if self._context.get('web_domain_widget') and hasattr(self, 'company_id'):
            for rec in res:
                rec.update({'company_name': self.browse(rec.get('id')).company_id.name})

        return res
    
