class Index {

    static initGoods() {
        document.body.querySelectorAll('#goods')
                .forEach( link => link.addEventListener('click', Index._clickHandlerGoods) );
    }

    static _clickHandlerGoods(event){
        event.preventDefault(); // запрещаем событие

        let path = event.target.href; // забираем путь
        let guid = window.getSectionGUID(path);

        $('th#goods_table_1 div').stop().animate({width: 0});
        $('th#goods_table_2 div').stop().animate({width: 0});
        $('th#goods_table_3 div').stop().animate({width: 0});
        $('th#goods_table_4 div').stop().animate({width: 0});
        $('th#goods_table_5 div').stop().animate({width: 0});
        $('th#goods_table_6 div').stop().animate({width: 0});

        $('th#cart_table_1 div').stop().animate({width: 0});
        $('th#cart_table_2 div').stop().animate({width: 0});
        $('th#cart_table_3 div').stop().animate({width: 0});
        $('th#cart_table_4 div').stop().animate({width: 0});
        $('th#cart_table_5 div').stop().animate({width: 0});
        $('th#cart_table_6 div').stop().animate({width: 0});
        $('th#cart_table_7 div').stop().animate({width: 0});

        jQuery("#goods_table").replaceWith("<div id=\"goods_table\"></div>");
        jQuery("#header_cart").replaceWith("<div id=\"header_cart\"></div>");
        jQuery("#goods_cart").replaceWith("<div id=\"goods_cart\"></div>");

        jQuery("#categories ul li a").addClass('disabled');

        if (typeof guid !== undefined) {
            jQuery.ajax({
                url: "ajax/get_goods/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success : function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result)
                    {
                        jQuery("#goods_table").replaceWith(json.goods_table);
                        jQuery("#header_cart").replaceWith(json.header_cart);
                        jQuery("#goods_cart").replaceWith(json.goods_cart);

                        $('#goods_cart').stop().animate({height: Number(json.cart_height)})

                        jQuery(window).scrollTop(0); // Скроллим страницу в начало

                        countHeightTableGoods(json.goods_table_guids);
                        countHeightTableCart(json.cart_table_guids);

                        updateTables();
                        widthHeadGoods();
                        widthHeadCart();

                    }
                    jQuery("#categories ul li a").removeClass('disabled');
                    document.body.querySelectorAll('#cart_add')
                        .forEach( link => link.addEventListener('click', Index._clickAddCart));
                    document.body.querySelectorAll('#cart_link_add')
                        .forEach( link => link.addEventListener('click', Index._clickQuantityAddCart));
                    document.body.querySelectorAll('#cart_link_reduce')
                        .forEach( link => link.addEventListener('click', Index._clickQuantityReduceCart));
                }
            });
        }
    }

    static _clickAddCart(event) {
        event.preventDefault(); // запрещаем событие

        let path = event.target.href; // забираем путь
        let guid = window.getProductGUID(path);

        jQuery("#header_cart").replaceWith("<div id=\"header_cart\"></div>");
        jQuery("#goods_cart").replaceWith("<div id=\"goods_cart\"></div>");

        if (typeof guid !== undefined) {
            jQuery.ajax({
                url: "ajax/cart_add/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success: function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result) {

                        jQuery("#header_cart").replaceWith(json.header_cart);
                        jQuery("#goods_cart").replaceWith(json.goods_cart);

                        countHeightTableCart(json.cart_table_guids);

                        updateTables();
                        widthHeadCart();
                    }
                }
            });
        }
    }

    static _clickQuantityAddCart(event) {
        event.preventDefault(); // запрещаем событие

        let path = event.target.href; // забираем путь
        let guid = window.getProductGUID(path);

        if (typeof guid !== undefined) {

            jQuery("#header_cart").replaceWith("<div id=\"header_cart\"></div>");

            jQuery.ajax({
                url: "ajax/cart_add_quantity/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success: function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result) {
                        jQuery("#td_cart_quantity" + guid).replaceWith(json.td_cart_quantity);
                        jQuery("#td_cart_total_price" + guid).replaceWith(json.td_cart_total_price);
                        jQuery("#td_cart_total_price_ruble" + guid).replaceWith(json.td_cart_total_price_ruble);
                        jQuery("#header_cart").replaceWith(json.header_cart);
                        document.body.querySelectorAll('#cart_link_add')
                            .forEach( link => link.addEventListener('click', Index._clickQuantityAddCart));
                        document.body.querySelectorAll('#cart_link_reduce')
                            .forEach( link => link.addEventListener('click', Index._clickQuantityReduceCart))
                    }
                }
            });
        }
    }

    static _clickQuantityReduceCart(event) {
        event.preventDefault(); // запрещаем событие

        let path = event.target.href; // забираем путь
        let guid = window.getProductGUID(path);

        if (typeof guid !== undefined) {

            jQuery("#header_cart").replaceWith("<div id=\"header_cart\"></div>");

            jQuery.ajax({
                url: "ajax/cart_reduce_quantity/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success: function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result) {
                        jQuery("#td_cart_quantity" + guid).replaceWith(json.td_cart_quantity);
                        jQuery("#td_cart_total_price" + guid).replaceWith(json.td_cart_total_price);
                        jQuery("#td_cart_total_price_ruble" + guid).replaceWith(json.td_cart_total_price_ruble);
                        if (json.delete) {
                            jQuery("#tr_cart" + guid).replaceWith("");
                        }
                        jQuery("#header_cart").replaceWith(json.header_cart);
                        document.body.querySelectorAll('#cart_link_add')
                            .forEach( link => link.addEventListener('click', Index._clickQuantityAddCart));
                        document.body.querySelectorAll('#cart_link_reduce')
                            .forEach( link => link.addEventListener('click', Index._clickQuantityReduceCart))
                    }
                }
            });
        }
    }

    static _clickQuantityDeleteCart(event) {
        event.preventDefault(); // запрещаем событие

        let path = event.target.href; // забираем путь
        let guid = window.getProductGUID(path);

        if (typeof guid !== undefined) {

            jQuery("#header_cart").replaceWith("<div id=\"header_cart\"></div>");

            jQuery.ajax({
                url: "ajax/cart_delete/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success: function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result) {

                        jQuery("#header_cart").replaceWith(json.header_cart);
                        jQuery("#tr_cart" + guid).replaceWith("");

                        countHeightTableCart(json.cart_table_guids);

                        updateTables();
                    }
                }
            });
        }
    }
}

Index.initGoods();

function getProductGUID(path) {
    var wheres_ = path.lastIndexOf("?product=");
    if (wheres_ !== 0) {
        return path.slice("?product=".length + wheres_, path.length);
    }
    return undefined
}

function getSectionGUID(path) {
    var wheres_ = path.lastIndexOf("?sections=");
    if (wheres_ !== 0) {
        return path.slice("?sections=".length + wheres_, path.length);
    }
    return undefined
}