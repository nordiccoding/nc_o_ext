 //static/src/js/first_module.js


 openerp.ah_module = function (instance) {
    instance.web.client_actions.add('ah_module.action', 'instance.odoo_web_module');
    instance.odoo_web_module = instance.web.Widget.extend({
        'template': 'odoo_web_module',
         events: {
             'click .html_elemet button': 'button_click',
             'keydown .html_elemet input': 'text_keypress'
         },
   button_click: function(){
    alert("Test!");
   },
   text_keypress: function(){
    alert("Entered Key in Text!");
   }
        
    });
 };
