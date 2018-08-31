class Index {

    static initGoods() {
        document.body.querySelectorAll('#goods')
                .forEach( link => link.addEventListener('click', Index._clickHandler) );
    }

    static _clickHandler(event){
        event.preventDefault(); // запрещаем событие

        let path = event.target.href; // забираем путь
        let guid = window.getGUID(path);

        $('#goods-table-th-1 div').stop().animate({width: 0});
        $('#goods-table-th-2 div').stop().animate({width: 0});
        $('#goods-table-th-3 div').stop().animate({width: 0});
        $('#goods-table-th-4 div').stop().animate({width: 0});
        $('#goods-table-th-5 div').stop().animate({width: 0});

        jQuery("#goods-table").replaceWith("<div id=\"goods-table\"></div>");

        jQuery("#categories ul li a").addClass('disabled');

        if (typeof guid !== 'undefined') {
            jQuery.ajax({
                url: "ajax/get_goods",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success : function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result)
                    {
                        jQuery("#goods-table").replaceWith(json.content); // Заменяем div
                        jQuery(window).scrollTop(0); // Скроллим страницу в начало
                        updateTable();
                        widthHeadTable();
                    }
                    jQuery("#categories ul li a").removeClass('disabled');
                }
            });
        }
    }
}

Index.initGoods();

function getGUID(path) {
    var wheres_sections = path.lastIndexOf("?sections=");
    if (wheres_sections !== 0) {
        return path.slice("?sections=".length + wheres_sections, path.length);
    }
    return 'undefined'
}