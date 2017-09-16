

//window.onload = removeCurrencySymbolInList


function j_version () {
    var jq_version = jQuery.fn.jquery
    console.log('Current jQuery version is: ' + jq_version );
    return jq_version;
};


var removeCurrencySymbolInList = function () {
  console.log('removeCurrencySymbolInList');
  var cur = odoo.session_info.currencies;
  cur[1].symbol = '';
};

// removeCurrencySymbolInList();

//test the extensions from 
//https://stackoverflow.com/questions/44332969/how-can-i-includeor-extend-odoo-core-function-from-listview-e-g-instance-web

odoo.ah_extensions = function(instance) {
    instance.web.ListView = instance.web.ListView.extend({
         init : function() {
                    this._super.apply(this, arguments);
                    console.log('BB extension worked!');
        },

    });
};