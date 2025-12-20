from odoo import models, fields, api

class CoursesScreen(models.Model):
    _name = 'courses.screen'
    _rec_name = 'name'

    name = fields.Char()
