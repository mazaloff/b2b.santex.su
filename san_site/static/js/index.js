class Index {

    static initGoods() {
        document.body.querySelectorAll('#goods')
                .forEach( link => link.addEventListener('click', Index._clickHandler) );
    }

    static _clickHandler(event){
        event.preventDefault(); // запрещаем событие

        let path = event.target.href; // забираем путь
        let guid = window.getGUID(path);

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
                        window.history.pushState({route: path}, "EVILEG", path); // устанавливаем URL в строку браузера
                        jQuery("#goods-table").replaceWith(json.content); // Заменяем div со списком статей на новый
                        jQuery(window).scrollTop(0); // Скроллим страницу в начало
                    }
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