class Index {

    static initGoods() {
        document.body.querySelectorAll('#goods')
                .forEach( link => link.addEventListener('click', Index._clickHandlerGoods) );
    }

    static _clickHandlerGoods(event){
        event.preventDefault(); // запрещаем событие

        let html_view_category = jQuery("#goods").html();
        let path = event.target.href; // забираем путь
        let guid = window.getSectionGUID(path);

        jQuery("#products").replaceWith(main_goods_html);

        widthHeadGoods();
        widthHeadCart();

        jQuery("#categories ul li a").addClass('disabled');

        jQuery.ajax({
            url: "ajax/get_goods/",
            type: 'GET',
            data: {'guid': guid},
            dataType: 'json', // забираем номер страницы, которую нужно отобразить

            success : function (json) {
                // Если запрос прошёл успешно и сайт вернул результат
                if (json.result)
                {
                    jQuery("#products").replaceWith(json.goods_html);

                    jQuery("#goods").html("<div id=\"goods\">" + html_view_category + "</div>");

                    history.pushState(null, null, '/');
                    history.replaceState(null, null, '/');

                    jQuery(window).scrollTop(0);

                    main_goods_table_guids = json.goods_table_guids;
                    main_cart_table_guids = json.cart_table_guids;

                    countHeightTableGoods();
                    countHeightTableCart();

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
                document.body.querySelectorAll('#goods')
                    .forEach( link => link.addEventListener('click', Index._clickHandlerGoods) );
            }
        });
    }

    static _clickAddCart(event) {
        event.preventDefault(); // запрещаем событие

        let path = event.target.href; // забираем путь
        let guid = window.getProductGUID(path);

        jQuery("#header_cart").replaceWith("<div id=\"header_cart\"></div>");
        jQuery("#goods_cart").replaceWith("<div id=\"goods_cart\"></div>");

        if (typeof guid !== undefined) {
            jQuery.ajax({
                url: "ajax/cart/add/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success: function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result) {

                        jQuery("#header_cart").replaceWith(json.header_cart);
                        jQuery("#goods_cart").replaceWith(json.goods_cart);

                        main_user = json.user_name;
                        main_cart_table_guids = json.cart_table_guids;

                        countHeightTableCart();

                        updateTables();
                        widthHeadCart();
                    }
                    document.body.querySelectorAll('#cart_link_add')
                        .forEach( link => link.addEventListener('click', Index._clickQuantityAddCart));
                    document.body.querySelectorAll('#cart_link_reduce')
                        .forEach( link => link.addEventListener('click', Index._clickQuantityReduceCart));
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
                url: "ajax/cart/add_quantity/",
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
                url: "ajax/cart/reduce_quantity/",
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
                url: "ajax/cart/delete/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success: function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result) {
                        jQuery("#header_cart").replaceWith(json.header_cart);
                        jQuery("#tr_cart" + guid).replaceWith("");
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