{
    'name': 'Menu for All BA',
    'category': 'account',
    'version': '1.0',
    'depends': ['base','stock'],
    'author': 'Port Cities',
    'description': '''
   add new menu in point of sale
   Author : Ardian Fajar Rahmanto
    ''',
    'data': [
        'views/ba_view_all_report.xml',
        'wizard/ba_report_all_view.xml',    
        'action_report.xml', 
    ],
    'installable': True,
    'active': False,
    'auto_install': False
}