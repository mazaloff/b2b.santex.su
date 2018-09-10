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
            dataType: 'json',

            success : function (json) {
                // Если запрос прошёл успешно и сайт вернул результат
                if (json.result)
                {
                    jQuery("#products").replaceWith(json.goods_html);

                    jQuery("#goods").html("<div id=\"goods\">" + html_view_category + "</div>");

                    history.pushState(null, null, '/');
                    history.replaceState(null, null, '/');

                    jQuery(window).scrollTop(0);

                    countHeightTableGoods();
                    countHeightTableCart();

                    updateTables();

                    widthHeadGoods();
                    widthHeadCart();
                } else {
                    console.error('Ошибка получения данных с сервера');
                }
                jQuery("#categories ul li a").removeClass('disabled');
                document.body.querySelectorAll('#goods')
                    .forEach( link => link.addEventListener('click', Index._clickHandlerGoods) );
            }
        });
    }

    static _clickAddCart(guid) {

        guid = window.getProductGUID(guid);

        jQuery("#cart").replaceWith("<div id=\"cart\"></div>");

        if (typeof guid !== undefined) {
            jQuery.ajax({
                url: "ajax/cart/add/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success: function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result) {

                        jQuery("#cart").replaceWith(json.cart_http);

                        countHeightTableCart();

                        updateTables();
                        widthHeadCart();
                    } else {
                        console.error('Ошибка получения данных с сервера');
                    }
                }
            });
        }
    }

    static _clickQuantityAddCart(guid) {

        guid = window.getProductGUID(guid);

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
                        jQuery("#td_cart_quantity" + guid).replaceWith(json.http_quantity);
                        jQuery("#td_cart_total_price" + guid).replaceWith(json.http_total_price);
                        jQuery("#td_cart_total_price_ruble" + guid).replaceWith(json.http_total_price_ruble);
                        jQuery("#header_cart").replaceWith(json.header_cart);
                    } else {
                        console.error('Ошибка получения данных с сервера');
                    }
                }
            });
        }
    }

    static _clickQuantityReduceCart(guid) {

        guid = window.getProductGUID(guid);

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
                        jQuery("#td_cart_quantity" + guid).replaceWith(json.http_quantity);
                        jQuery("#td_cart_total_price" + guid).replaceWith(json.http_total_price);
                        jQuery("#td_cart_total_price_ruble" + guid).replaceWith(json.http_total_price_ruble);
                        if (json.delete) {
                            jQuery("#tr_cart" + guid).replaceWith("");
                            countHeightTableCart();
                            updateTables();
                        } else {
                            console.error('Ошибка получения данных с сервера');
                        }
                        jQuery("#header_cart").replaceWith(json.header_cart);
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
                    } else {
                        console.error('Ошибка получения данных с сервера');
                    }
                }
            });
        }
    }
}

Index.initGoods();

function getProductGUID(path) {

    let arrayOfStrings = path.split('/');
    if (arrayOfStrings.length !== 0) {
        return arrayOfStrings[arrayOfStrings.length - 1];
    }

    return undefined
}

function getSectionGUID(path) {

    let wheres_ = path.lastIndexOf("?sections=");
    if (wheres_ !== 0) {
        return path.slice("?sections=".length + wheres_, path.length);
    }
    return undefined
}