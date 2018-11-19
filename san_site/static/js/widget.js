
let id_delivery = $( "#id_delivery" );
let id_begin_date = $( "#id_begin_date" );
let id_end_date = $( "#id_end_date" );

id_delivery.datepicker($.datepicker.regional[ "ru" ]);
id_begin_date.datepicker($.datepicker.regional[ "ru" ]);
id_end_date.datepicker($.datepicker.regional[ "ru" ]);

id_delivery.datepicker( "option", "defaultDate", + 1 );
id_delivery.datepicker( "option", "minDate", "+1d" );
id_delivery.datepicker( "option", "maxDate", "+7d" );

id_begin_date.datepicker( "option", "onSelect", onSelectBeginDate );
id_end_date.datepicker( "option", "onSelect", onSelectEndDate );

function onSelectBeginDate(date) {
    id_begin_date.datepicker( "hide" );
    Index._changeFiltersOfOrdersList(date, id_end_date.datepicker( "getDate" ).toLocaleDateString());
}
function onSelectEndDate(date) {
    id_end_date.datepicker( "hide" );
    Index._changeFiltersOfOrdersList(id_begin_date.datepicker( "getDate" ).toLocaleDateString(), date);
}
