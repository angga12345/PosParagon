# -*- coding: utf-8 -*-
{
    'name'          : 'POS Stock Report',
    'version'       : '1.0',
    'summary'       : 'Create template for POS stock report',
    'sequence'      : 10,
    "author"        : "Portcities",
    'description'   : """
                        author : Wahyu Setiawati
                        
                        v.1.0 : \n
                        make Template Report for Stock from POS backend
                      """,
    'category'      : 'reports',
    'depends'       : ['stock', 'point_of_sale'],
    'data'          : [
                       'report_menu.xml',
                       'views/stock_report_action.xml',
                       'views/stock_report_view.xml', 
                      ],
    'installable'   : True,
    'application'   : True,
    'auto_install'  : False,
}
