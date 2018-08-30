'use strict';

// Модуль приложения
var app = (function($) {

    // Инициализируем нужные переменные
    var ajaxUrl = 'ajax/get_categories',
        ui = {
            $categories: $('#categories'),
            $goods: $('#goods')
        };

    // Инициализация дерева категорий с помощью jstree
    function _initTree(data) {
        var category;
        ui.$categories.jstree({
            core: {
                check_callback: true,
                multiple: false,
                data: data
            },
            types: {
                default : {
                    valid_children : ["default","file"]
                },
            }

        }).bind('changed.jstree', function(e, data) {

            category = data.node.text;
            var str_html = 'Товары из категории ' + category;
            ui.$goods.html(str_html.link('?sections=' + data.node.original.href));
            console.log('changed node: ', data);

            var guid = data.node.original.href;

            jQuery.ajax({
                url: "ajax/get_goods",
                type: 'GET',
                data: {'guid': guid},
                dataType: 'json', // забираем номер страницы, которую нужно отобразить

                success : function (json) {
                    // Если запрос прошёл успешно и сайт вернул результат
                    if (json.result)
                    {
                        //window.history.pushState({route: path}, "EVILEG", path); // устанавливаем URL в строку браузера
                        jQuery("#goods-table").replaceWith(json.content); // Заменяем div со списком статей на новый
                        jQuery(window).scrollTop(0); // Скроллим страницу в начало
                    }
                }
            });
        });
    }

    // Загрузка категорий с сервера
    function _loadData() {
        var params = {
            action: 'get_categories'
        };

        $.ajax({
            url: ajaxUrl,
            method: 'GET',
            data: params,
            dataType: 'json',
            success: function(resp) {
                // Инициализируем дерево категорий
                if (resp.code === 'success') {
                    _initTree(resp.result);
                } else {
                    console.error('Ошибка получения данных с сервера: ', resp.message);
                }
            },
            error: function(error) {
                console.error('Ошибка: ', error);
            }
        });
    }

    // Инициализация приложения
    function init() {
        _loadData();
    }

    // Экспортируем наружу
    return {
        init: init
    }

})(jQuery);

jQuery(document).ready(app.init);