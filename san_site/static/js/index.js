class Index {

    static initGoods() {
        document.body.querySelectorAll('#goods')
                .forEach( link => link.addEventListener('click', Index._clickHandlerGoods) );
    }

    static _clickHandlerGoods(event){
        event.preventDefault(); // запрещаем событие

        let path = event.target.href; // забираем путь
        let guid = window.getCategoriesGUID(path);

        $('th#goods_table_1 div').stop().animate({width: 0});
        $('th#goods_table_2 div').stop().animate({width: 0});
        $('th#goods_table_3 div').stop().animate({width: 0});
        $('th#goods_table_4 div').stop().animate({width: 0});
        $('th#goods_table_5 div').stop().animate({width: 0});
        $('th#goods_table_6 div').stop().animate({width: 0});

        jQuery("#goods_table").replaceWith("<div id=\"goods_table\"></div>");

        jQuery("#categories ul li a").addClass('disabled');

        if (typeof guid !== 'undefined') {
            jQuery.ajax({
                url: "ajax/get_goods/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success : function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result)
                    {
                        jQuery("#goods_table").replaceWith(json.content); // Заменяем div
                        jQuery(window).scrollTop(0); // Скроллим страницу в начало
                        updateTable();
                        widthHeadTable();
                    }
                    jQuery("#categories ul li a").removeClass('disabled');
                }
            });
        }
    }

    static _clickAddCart(event) {
        event.preventDefault(); // запрещаем событие

        let path = event.target.href; // забираем путь
        let guid = window.getAddCartGUID(path);

        jQuery.ajax({
            url: "ajax/cart_add/",
            type: 'GET',
            data: {'guid': guid},
            dataType: 'json', // забираем номер страницы, которую нужно отобразить

            success : function (json) {
                // Если запрос прошёл успешно и сайт вернул результат
                if (json.result)
                {
                }
            }
        });
    }
}

Index.initGoods();

function getAddCartGUID(path) {
    var wheres_sections = path.lastIndexOf("?product=");
    if (wheres_sections !== 0) {
        return path.slice("?product=".length + wheres_sections, path.length);
    }
    return 'undefined'
}

function getCategoriesGUID(path) {
    var wheres_sections = path.lastIndexOf("?sections=");
    if (wheres_sections !== 0) {
        return path.slice("?sections=".length + wheres_sections, path.length);
    }
    return 'undefined'
}