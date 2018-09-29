$.datepicker.setDefaults({
});
let id_delivery = $( "#id_delivery" );

id_delivery.datepicker($.datepicker.regional[ "ru" ]);

$.datepicker.setDefaults({
    defaultDate: +1,
    minDate: "+1d",
    maxDate: "+7d"
});

id_delivery.datepicker( "option", "buttonImage", "/static/img/cal.gif" );