$.datepicker.setDefaults({
});

$( "#id_delivery" ).datepicker($.datepicker.regional[ "ru" ]);

$.datepicker.setDefaults({
    defaultDate: +1,
    minDate: "+1d",
    maxDate: "+7d"
});