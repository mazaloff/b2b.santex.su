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
        recoverOnlyStock();
        recoverOnlyPromo();

        jQuery("#categories ul li a").addClass('disabled');
        jQuery("#loading_icon").removeClass('disabled');

        document.getElementById('goods_table').style.display = 'none';

        jQuery.ajax({
            url: "ajax/get_goods/",
            type: 'GET',
            data: {
                'guid': guid,
                'only_stock': getOnlyStock(),
                'only_promo': getOnlyPromo()
            },
            dataType: 'json',

            success : function (json) {
                // Если запрос прошёл успешно и сайт вернул результат
                if (json.result)
                {
                    jQuery("#products").replaceWith(json.goods_html);
                    recoverOnlyStock();
                    recoverOnlyPromo();

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
                jQuery("#loading_icon").addClass('disabled');
                document.body.querySelectorAll('#goods')
                    .forEach(link => link.addEventListener('click', Index._clickHandlerGoods));
                onlyStock();
                onlyPromo();
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

    static _changeSelections() {

        jQuery("#goods_table").replaceWith("<div id=\"goods_table\"></div>");
        jQuery("#categories ul li a").addClass('disabled');
        jQuery("#loading_icon").removeClass('disabled');

        jQuery.ajax({
            url: "ajax/selection/",
            type: 'GET',
            data: {
                'only_stock': getOnlyStock(),
                'only_promo': getOnlyPromo(),
                'search': getSearchCode()
            },
            dataType: 'json',

            success: function (json) {
                // Если запрос прошёл успешно и сайт вернул результат
                if (json.result) {
                    jQuery("#goods_table").replaceWith(json.goods_html);

                    if (json.section.guid === undefined) {
                        jQuery("#goods").html('Выберите категорию товаров...');
                    } else {
                        jQuery("#goods").html('Товары из категории ' + json.section.name
                            .link('?sections=' + json.section.guid));
                    }

                    jQuery(window).scrollTop(0);

                    countHeightTableGoods();
                    updateTables();
                    widthHeadGoods();

                } else {
                    console.error('Ошибка получения данных с сервера');
                }
                jQuery("#categories ul li a").removeClass('disabled');
                jQuery("#loading_icon").addClass('disabled');
            }
        });

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