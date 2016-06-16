# -*- coding: utf-8 -*-

from openerp import models, fields, api

class HumanNameTerm(models.Model):  
    _name = "hc.human.name.term" 
    _description = "Human Name Term"
    _inherit = ["res.partner.title"]         

    name = fields.Char(
        string="Human Name Term", 
        help="A single term (part) of a human name (e.g., John, Smith).")

    _sql_constraints = [
        ("name_unique",
        "UNIQUE(name)",
        "The term must be unique.")
        ]

class SuffixHumanName(models.Model):    
    _name = "hc.human.name.suffix"   
    _description = "Human Name Suffix"      
    _inherit = ["res.partner.title"]     

    name = fields.Char(
        string="Suffix Human Name Term", 
        help="Parts that come after the name. Aka post-nominal letters. May be a family title (e.g., Jr.) a credential (e.g., RN), a title (.e.g., OBE), or a degree (e.g., PhD).")

class HumanName(models.Model):

    _name = "hc.human.name"
    _description = "Human Name"
    
    use = fields.Selection(string="Human Name Use", 
        selection=[
            ("usual", "Usual"), 
            ("official", "Official"),
            ("temp", "Temp"),
            ("nickname", "Nickname"),
            ("anonymous", "Anonymous"),
            ("old", "Old"),
            ("maiden", "Maiden")],
        default="usual",
        help="The use of a human name.")
    name = fields.Char(
        store=True,
        string="Full Name",
        help="A full text representation of the human name.")
    given = fields.Char(
        store=True,
        string="Given Name", 
        readonly=True,
        help="Given names (not always 'first'). Includes middle names.")
    family = fields.Char(
        store=True,
        string="Family Name", 
        readonly=True,
        help="The parts of a name that links to the genealogy. (e.g., surname, birth last name).")
    prefix_ids = fields.Many2many(
        comodel_name="res.partner.title", 
        string="Prefix Names", 
        help="Parts that come before the name.")
    first_id = fields.Many2one(
        comodel_name="hc.human.name.term", 
        string="First Name", 
        help="Part of given name.")
    middle_ids = fields.Many2many(
        comodel_name="hc.human.name.term", 
        relation="middle_name_human_term_rel", 
        string="Middle Names", 
        help="Part of given name.")
    initial_ids = fields.Many2many(
        comodel_name="hc.human.name.term", 
        relation="initial_name_human_term_rel", 
        string="Initial Names", 
        help="Part of given name.")
    nickname_ids = fields.Many2many(
        comodel_name="hc.human.name.term", 
        relation="nickname_human_term_rel", 
        string="Nicknames", 
        help="Part of given name.")
    surname_id = fields.Many2one(
        comodel_name="hc.human.name.term", 
        string="Surname", 
        help="Part of family name.")
    previous_last_id = fields.Many2one(
        comodel_name="hc.human.name.term", 
        string="Previous Surname", 
        help="Part of family name (e.g., previous married family name).")
    suffix_ids = fields.Many2many(
        comodel_name="hc.human.name.suffix", 
        string="Suffix Names", 
        help="Parts that come after the name.")
    preferred_name = fields.Char(
        string="Preferred Name", 
        help="How the person prefers to be addressed in a conversation (e.g., John, Mr. Smith).")
    mother_maiden_name_id = fields.Many2one(
        comodel_name="hc.human.name.term", 
        string="Mother Maiden Name", 
        help="Mother's surname at birth. Part of the family name.")
    birth_last_name_id = fields.Many2one(
        comodel_name="hc.human.name.term", 
        string="Birth Last Name", 
        help="Person's surname at birth.")
    display_order = fields.Selection(string="Display Name Order", 
        selection=[
            ("given maiden last", "Given Maiden Last (e.g., American name)"), 
            ("maiden last first", "Maiden Last First (e.g., Chinese name)"),
            ("first last maiden", "First Last Maiden (e.g., Spanish name)")],
        default="given maiden last",
        help="The display order of this human name.")

# class HcExtensionHumanNameFull(models.Model):
#     _inherit = 'hc.human.name'

#     @api.depends('first_id','surname_id')
#     def compute_full(self):
#         full = ''
#         lines = ''
#         first = self.first_id and ', '+self.first_id.name or ''
#         surname = self.surname_id and ', '+self.surname_id.name or ''
#         lines = first+surname+lines
#         self.name = lines

#     name = fields.Char(
#         compute='compute_full', 
#         store=True,
#         string="Full Name",
#         help="A full text representation of the human name.")

# class HcExtensionHumanNameFamily(models.Model):
#     _inherit = 'hc.human.name'

#     @api.depends('mother_maiden_name_id','surname_id')
#     def compute_family(self):
#         family = ''
#         lines = ''
#         maiden = self.mother_maiden_name_id and ', '+self.mother_maiden_name_id.name or ''
#         surname = self.surname_id and ', '+self.surname_id.name or ''
#         lines = maiden+surname+lines
#         self.name = lines

#     family = fields.Char(
#         compute="compute_family",
#         store=True,
#         string="Family Name", 
#         help="Family name (often called 'Surname').")

# Requirements

# No mandatory fields

# compute: Given = First Name + Middle Names + Initial Names + "(" + Nicknames +")"
# compute: Family = Mother Maiden Name + Birth Name + Previous Name + Last Name
# compute: Family_Reverse = Birth Name + Previous Name + Last Name + Mother Maiden Name
# compute: Full = Prefix + Given + Family + Suffix
# compute: Full_Reverse = Prefix + Family + Given + Suffix
# compute: Full_Family_Reverse = Prefix + Given + Family_Reverse + Suffix

class HcExtensionHumanName(models.Model):
    _inherit = 'hc.human.name'

    @api.model
    def create(self, vals):

        first = self.env['hc.human.name.term'].browse(vals['first_id']).name
        # middle = self.env['hc.human.name.term'].browse(vals['middle_ids']).name
        last = self.env['hc.human.name.term'].browse(vals['surname_id']).name
        maiden = self.env['hc.human.name.term'].browse(vals['mother_maiden_name_id']).name
        full = first+' '+last
        # full_first = first+' '+middle
        full_family = maiden+' '+last
        vals['name'] = full
        # vals['given'] = full_first
        vals['family'] = full_family

        return super(HcExtensionHumanName, self).create(vals)

    @api.multi
    def write(self, vals):
       
        if 'first_id' in vals:   
            first = self.env['hc.human.name.term'].browse(vals['first_id']).name
        else:
            first = self.first_id.name

        # if 'middle_ids' in vals:   
        #     middle = self.env['hc.human.name.term'].browse(vals['middle_ids']).name
        # else:
        #     middle = self.middle_ids.name

        if 'mother_maiden_name_id' in vals:    
            maiden = self.env['hc.human.name.term'].browse(vals['mother_maiden_name_id']).name
        else:
            maiden = self.mother_maiden_name_id.name    

        if 'surname_id' in vals:    
            last = self.env['hc.human.name.term'].browse(vals['surname_id']).name
        else:
            last = self.surname_id.name

        full = first+' '+last
        # full_first = first+' '+middle
        full_family = maiden+' '+last
        vals['name'] = full
        # vals['given'] = full_first
        vals['family'] = full_family

        return super(HcExtensionHumanName, self).create(vals)