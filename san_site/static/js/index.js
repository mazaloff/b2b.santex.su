class Index {

    constructor(name) {
        this.currentElem = null;
    }

    static initGoods() {
        document.body.querySelectorAll('#goods')
            .forEach(link => link.addEventListener('click', Index._clickHandlerGoods));
    }

    static _clickHandlerGoods(event) {
        event.preventDefault();

        let html_view_category = jQuery("#goods").html();
        if (html_view_category === '') {
            return
        }
        let path = event.target.href;
        let guid = window.getSectionGUID(path);

        jQuery("#products").replaceWith(main_products);

        $('#only_promo').prop('checked', false);
        createCookie('is_only_promo', getOnlyPromo(), 30);

        recoverOnlyStock();

        history.pushState(null, null, '/');
        history.replaceState(null, null, '/');

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

            success: function (json) {
                // Если запрос прошёл успешно и сайт вернул результат
                if (json.success) {
                    jQuery("#products").replaceWith(json.products);

                    recoverOnlyStock();

                    jQuery("#goods").html('Товары из категории <strong>' + json.current_section
                        .link('?sections=' + guid) + '</strong>');

                    jQuery(window).scrollTop(0);

                    countHeightTableGoods();
                    countHeightTableCart();

                    updateTables();

                    widthHeadGoods();
                    widthHeadCart();

                    jQuery("#categories ul li a").removeClass('disabled');
                    jQuery("#loading_icon").addClass('disabled');
                    document.body.querySelectorAll('#goods')
                        .forEach(link => link.addEventListener('click', Index._clickHandlerGoods));
                    onlyStock();
                    onlyPromo();
                } else {
                    console.error('Ошибка получения данных с сервера');
                }
            }
        });
    }

    static _showFormForQuantity(guid) {

        guid = window.getProductGUID(guid);

        if (typeof guid !== undefined) {
            jQuery.ajax({
                url: "ajax/cart/get_form_quantity/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success: function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.success) {

                        let form_enter_quantity = jQuery("#form_enter_quantity");

                        form_enter_quantity.replaceWith(json.form_enter_quantity);
                        form_enter_quantity.show();

                        let black_overlay = jQuery('.black-overlay');
                        black_overlay.fadeOut(10);
                        black_overlay.fadeIn(500);

                        let position = getOffset(document.getElementById('tr_goods' + guid));
                        position.left += $("th#goods_table_1").width();
                        position.left += Math.ceil($("th#goods_table_2").width() / 2);
                        let form_enter_wrapper = jQuery(".enter-quantity-wrapper");
                        form_enter_wrapper.css('left', position.left - 80);
                        form_enter_wrapper.css('top', position.top - 0);
                        jQuery("#id_quantity").focus();

                        jQuery("#tr_goods" + guid).addClass('current-tr');

                        $("#btn_enter_quantity_cart").click(
                            () => {
                                let quantity = jQuery("#id_quantity").val();
                                AddCart(guid, quantity);
                                return false;
                            }
                        );
                    } else {
                        console.error('Ошибка получения данных с сервера');
                    }
                }
            });
        }
    }

    static _helpQuantity(guid) {
        let help_tip = jQuery('#tr_goods' + guid + ' .help-tip');
        help_tip.show();

        let black_overlay = jQuery('.black-overlay');
        black_overlay.fadeOut(10);
        black_overlay.fadeIn(500);

        let position = getOffset(document.getElementById('tr_goods' + guid));
        help_tip.css('top', position.top);
    }

    static _closeBlackOverlay(guid) {
        jQuery('#tr_goods' + guid).removeClass('current-tr');
        jQuery('#form_enter_quantity').hide();
        jQuery('.black-overlay').fadeOut(0);
    }

    static _closeBlackOverlayHelp() {
        jQuery('.help-tip').hide();
        jQuery('.black-overlay').fadeOut(0);
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
                    if (json.success) {
                        jQuery("#td_cart_quantity" + guid).replaceWith(json.td_cart_quantity);
                        jQuery("#td_cart_total_price" + guid).replaceWith(json.td_cart_total_price);
                        jQuery("#td_cart_total_price_ruble" + guid).replaceWith(json.td_cart_total_price_ruble);
                        jQuery("#header_cart").replaceWith(json.header_cart);
                        jQuery("#user_cart").replaceWith(json.user_cart);
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
                    if (json.success) {
                        jQuery("#td_cart_quantity" + guid).replaceWith(json.td_cart_quantity);
                        jQuery("#td_cart_total_price" + guid).replaceWith(json.td_cart_total_price);
                        jQuery("#td_cart_total_price_ruble" + guid).replaceWith(json.td_cart_total_price_ruble);
                        if (json.delete) {
                            jQuery("#tr_cart" + guid).replaceWith("");
                            countHeightTableCart();
                            updateTables();
                        } else {
                            console.error('Ошибка получения данных с сервера');
                        }
                        jQuery("#header_cart").replaceWith(json.header_cart);
                        jQuery("#user_cart").replaceWith(json.user_cart);
                    }
                }
            });
        }
    }

    static _clickDeleteRowCart(guid) {

        guid = window.getProductGUID(guid);

        if (typeof guid !== undefined) {

            jQuery("#header_cart").replaceWith("<div id=\"header_cart\"></div>");

            jQuery.ajax({
                url: "ajax/cart/delete_row/",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success: function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.success) {
                        jQuery("#tr_cart" + guid).replaceWith("");
                        countHeightTableCart();
                        updateTables();
                    } else {
                        console.error('Ошибка получения данных с сервера');
                    }
                    jQuery("#header_cart").replaceWith(json.header_cart);
                    jQuery("#user_cart").replaceWith(json.user_cart);
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
                if (json.success) {
                    jQuery("#goods_table").replaceWith(json.products);

                    if (json.section.guid === undefined) {
                        jQuery("#goods").html('Выберите категорию товаров...');
                    } else {
                        jQuery("#goods").html('Товары из категории <strong>' + json.section.name
                            .link('?sections=' + json.section.guid) + '</strong>');
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

    static _changeFiltersOfOrdersList(begin_date, end_date) {

        jQuery("#list_orders").replaceWith("<div id=\"list_orders\"></div>");

        jQuery.ajax({
            url: "ajax/order/get_orders_list/",
            type: 'GET',
            data: {
                'begin_date': begin_date,
                'end_date': end_date
            },
            dataType: 'json',

            success: function (json) {
                // Если запрос прошёл успешно и сайт вернул результат
                if (json.success) {
                    jQuery("#list_orders").replaceWith(json.list_orders);

                    jQuery(window).scrollTop(0);

                    updateTables();
                    widthHeadOrders();

                } else {
                    console.error('Ошибка получения данных с сервера');
                }
            }
        });
    }
}

Index.initGoods();

function AddCart(guid, quantity) {

    jQuery("#form_enter_quantity").hide();
    jQuery('.black-overlay').fadeOut(0);

    jQuery("#tr_goods" + guid).removeClass('current-tr');

    if (quantity === '' || quantity === '0') {
        jQuery("#id_quantity").focus();
        return
    }

    jQuery("#cart").replaceWith("<div id=\"cart\"></div>");

    if (typeof guid !== undefined) {
        jQuery.ajax({
            url: "ajax/cart/add/",
            type: 'GET',
            data: {'guid': guid, 'quantity': quantity},
            dataType: 'json', // забираем номер страницы, которую нужно отобразить

            success: function (json) {
                // Если запрос прошёл успешно и сайт вернул результат
                if (json.success) {

                    jQuery("#cart").replaceWith(json.cart);
                    jQuery("#user_cart").replaceWith(json.user_cart);

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

function getOffset(el) {
    el = el.getBoundingClientRect();
    return {
        left: el.left + window.scrollX,
        top: el.top + window.scrollY
    }
}
