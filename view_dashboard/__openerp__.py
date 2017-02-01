# Part of LAZERP. See LICENSE file for full copyright and licensing details.
{
    'name': 'generic pci dasboard view 9',
    'version': '1.0',
    'depends': ["base","web","web_kanban","stock"],
    'author': 'Port Cities International',
    'description': """
v1.0
----
* filter page in kanban view.
* Author : Ryan Yunus
        

    """,
    'website': 'http://www.portcitiesindonesia.com',
    'category': 'Web',
    'sequence': 1,
    'data': ['views/templates.xml',
#              'data/data.xml',
             ],
    # 'qweb': [
    #          'static/src/xml/base.xml',
    #          'static/src/xml/web_planner.xml',
    #          'static/src/xml/systray.xml',
             
    #          ],          
    'auto_install': False,
    'installable': True,
    'application': False,
}
