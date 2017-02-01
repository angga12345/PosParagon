from openerp import models, fields, api, _
import random


class posconfig(models.Model):
    _inherit = "pos.config"
    
    @api.model
    def create(self,values):
        name = values.get('name')
        account_journal = self.create_account(name)
        journal_ids = []
        for id_account in account_journal:
            journal_ids.append(id_account.id)
        values['journal_ids'] = [(6,0,journal_ids)]
        res = super(posconfig,self).create(values)
        return res
    
    def short_code_account_account(self,name):
#       take 3 char in first word
        take3char_first_word = name[0:3].upper()
#       take first char til end of char
#         take_first_char = "".join([s[:1].upper() for s in name.split(' ')])
#       take only second char until end of character
#         notake1char = take_first_char[1:len(take_first_char)]
        random_number = random.randint(1,9999)
        return take3char_first_word+'-'+str(random_number)
    
    def take_value_name_pos_store(self):
        return self.name
    
    def create_account_debitcredit(self,name,code,tags_ids):
        dnc = self.env['account.account.type'].search([('name','=','Bank and Cash')])
        print name, 111111111111111111
        print code
        print tags_ids
        value = {'name':name+' '+'Debit',
                 'code':'POS'+'-'+code+'-'+'DEBIT',
                 'user_type_id':dnc.id,
                 'tag_ids':[(6,0,tags_ids)] }
        return self.env['account.account'].create(value)
    
    def create_account_profit(self,name,code,tags_ids):
        profit = self.env['account.account.type'].search([('name','=','Income')])
        value = {'name':name+' '+'Profit',
                 'code':'POS'+'-'+code+'-'+'P',
                 'user_type_id':profit.id,
                 'tag_ids':[(6,0,tags_ids)]}
        return self.env['account.account'].create(value)
    
    def create_account_loss(self,name,code,tags_ids):
        loss = self.env['account.account.type'].search([('name','=','Depreciation')])
        value = {'name':name+' '+'Loss',
                 'code':'POS'+'-'+code+'-'+'L',
                 'user_type_id':loss.id,
                 'tag_ids':[(6,0,tags_ids)]}
        return self.env['account.account'].create(value)
    
    def create_account(self,name):
#         name = self.take_value_name_pos_store()
        code = self.short_code_account_account(name)
        tags = self.env['account.account.tag'].search([('name','=','Point of Sale')],limit=1)
        
        tags_ids = []
        tags_ids.append(tags.id)
        
        debit = self.create_account_debitcredit(name,code,tags_ids)
        profit = self.create_account_profit(name,code,tags_ids)
        loss = self.create_account_loss(name,code,tags_ids)
        
        account_cash = self.create_account_journal_cash(name, code, debit.id, profit.id, loss.id)
        account_bank = self.create_account_journal_bank(name, code, debit.id)
        
        return account_cash,account_bank
    
    def create_account_journal_cash(self,name,code, debit_id, profit_id, loss_id):
        value_cash = {
                 'name':name+' '+'Cash Payment',
                 'ending_date_type':'today',
                 'type':'cash',
                 'code':'POS'+'-'+code+'-'+'CASH',
                 'journal_user': True,
                 'default_debit_account_id': debit_id,
                 'default_credit_account_id' : debit_id,
                 'profit_account_id': profit_id,
                 'loss_account_id': loss_id,
                 }
        return self.env['account.journal'].create(value_cash)
        
       
    def create_account_journal_bank(self,name,code,debit_id):
        value_bank = {
                 'name':name+' '+'Debit/Credit Payment',
                 'type':'bank',
                 'ending_date_type':'today',
                 'code':'POS'+'-'+code+'-'+'BANK',
                 'journal_user': True,
                 'default_debit_account_id': debit_id,
                 'default_credit_account_id' : debit_id
                 }
        return self.env['account.journal'].create(value_bank) 