from san_site.models import get_customer, Section, Currency, CustomersFiles
from django.contrib.auth.models import User
from django.conf import settings
import os

from openpyxl import Workbook
from openpyxl.styles import Font, colors
from openpyxl.styles import NamedStyle


def create_directory(path):
    if os.path.exists(path) and not os.path.isdir(path):
        print(f'Error: {path} - is not a directory')
        os.remove(path)
        print(f'Error: file with name {path} - was remove')
    if not os.path.exists(path):
        os.mkdir(path)
        print(f'Information: Directory with name {path} - was created')


def write_files(path_files_customer, user=None):
    courses = {}
    currency = Currency.objects.all()
    for elem in currency:
        courses[elem.id] = elem.get_today_course()

    path_file_csv = os.path.join(path_files_customer, 'goods_b2b_santex.csv')
    path_file_xls = os.path.join(path_files_customer, 'goods_b2b_santex.xlsx')
    sections = Section.objects.filter(group__isnull=True, is_deleted=False).order_by('name')

    if os.path.exists(path_file_xls) and os.path.isfile(path_file_xls):
        try:
            os.remove(path_file_xls)
        except FileNotFoundError:
            pass

    if user:
        list_str = ['Артикул;Название;Бренд;Штрихкод;Остаток;Базовая цена;Валюта;Цена руб;РРЦ руб;Уд.склад;В пути' + '\n']
    else:
        list_str = ['Артикул;Название;Бренд;Штрихкод;Остаток;Уд.склад;В пути' + '\n']

    workbook = Workbook()
    sheet = workbook.active

    header_style = NamedStyle(name="header")
    header_style.font = Font(bold=True, color=colors.RED, size=12)

    section_style = NamedStyle(name="section")
    section_style.font = Font(bold=True, color=colors.BLUE, size=12)

    sheet.column_dimensions[str(chr(64 + 1))].width = 15
    sheet.column_dimensions[str(chr(64 + 2))].width = 65
    sheet.column_dimensions[str(chr(64 + 3))].width = 15
    sheet.column_dimensions[str(chr(64 + 4))].width = 15
    sheet.column_dimensions[str(chr(64 + 5))].width = 10
    if user:
        sheet.column_dimensions[str(chr(64 + 6))].width = 13
        sheet.column_dimensions[str(chr(64 + 7))].width = 7
        sheet.column_dimensions[str(chr(64 + 8))].width = 13
        sheet.column_dimensions[str(chr(64 + 9))].width = 13
        sheet.column_dimensions[str(chr(64 + 5))].width = 10
        sheet.column_dimensions[str(chr(64 + 5))].width = 10
    else:
        sheet.column_dimensions[str(chr(64 + 5))].width = 10
        sheet.column_dimensions[str(chr(64 + 5))].width = 10

    sheet['A1'] = 'Артикул'
    sheet['B1'] = 'Название'
    sheet['C1'] = 'Бренд'
    sheet['D1'] = 'Штрихкод'
    sheet['E1'] = 'Остаток'
    if user:
        sheet['F1'] = 'База цена'
        sheet['G1'] = 'Вал.'
        sheet['H1'] = 'Цена руб.'
        sheet['I1'] = 'РРЦ руб.'
        sheet['J1'] = 'Уд.склад'
        sheet['K1'] = 'В пути'
    else:
        sheet['F1'] = 'Уд.склад'
        sheet['G1'] = 'В пути'

    header_row = sheet[1]
    for cell in header_row:
        cell.style = header_style

    row = 2
    for obj_section in sections:

        goods_list = obj_section.get_goods_list_section(user=user, only_stock=True)

        if len(goods_list) > 0:
            sheet[f'A{row}'] = obj_section.name
            sheet[f'A{row}'].style = section_style
            row += 1

        for elem in goods_list:
            code = elem['code'].replace(';', '').replace('"', '')
            barcode = elem['barcode'].replace(';', '').replace('"', '')
            name = elem['name'].replace(';', '').replace('"', '')
            brand = elem['brand'].replace(';', '').replace('"', '')
            quantity = str(0 if elem['quantity'] == '' else elem['quantity']).replace('>', '')
            remote = str(0 if elem['remote'] == '' else elem['remote']).replace('>', '')
            inway = str(0 if elem['inway'] == '' else elem['inway']).replace('>', '')
            price = 0 if elem['price'] == '' else elem['price']
            price_rrp = 0 if elem['price_rrp'] == '' else elem['price_rrp']
            discount = 0 if elem['discount'] == '' else elem['discount']
            currency = 'RUB' if elem['price_currency'].lower() == 'руб' else elem['price_currency'].upper()
            course = courses.get(elem['currency_id'], {'course': 1, 'multiplicity': 1})
            price_rub = round(discount * course['course'] / course['multiplicity'], 2)

            # for csv
            if user:
                list_str.append(f'{code};{name};{brand};{barcode};{quantity};{price};{currency};{price_rub};{price_rrp};{remote};{inway}' + '\n')
            else:
                list_str.append(f'{code};{name};{brand};{barcode};{quantity};{remote};{inway}' + '\n')

            # for excel
            sheet[f'A{row}'] = code
            sheet[f'B{row}'] = name
            sheet[f'C{row}'] = brand
            sheet[f'D{row}'] = barcode
            sheet[f'E{row}'] = int(quantity)
            if user:
                sheet[f'F{row}'] = price
                sheet[f'G{row}'] = currency
                sheet[f'H{row}'] = price_rub
                sheet[f'I{row}'] = price_rrp
                sheet[f'J{row}'] = int(remote)
                sheet[f'K{row}'] = int(inway)
            else:
                sheet[f'F{row}'] = int(remote)
                sheet[f'G{row}'] = int(inway)
            row += 1

    sheet.title = 'stocks'
    sheet.freeze_panes = 'A2'

    sheet.auto_filter.ref = sheet.dimensions

    # workbook.close()
    workbook.save(filename=path_file_xls)

    with open(path_file_csv, mode='w', encoding='utf-8-sig') as file:
        file.writelines(list_str)

def write_files_with_reserve(path_files_customer, user=None):
    courses = {}
    currency = Currency.objects.all()
    for elem in currency:
        courses[elem.id] = elem.get_today_course()

    path_file_csv = os.path.join(path_files_customer, 'goods_b2b_santex.csv')
    path_file_xls = os.path.join(path_files_customer, 'goods_b2b_santex.xlsx')
    sections = Section.objects.filter(group__isnull=True).order_by('name')

    if os.path.exists(path_file_xls) and os.path.isfile(path_file_xls):
        try:
            os.remove(path_file_xls)
        except FileNotFoundError:
            pass

    if user:
        list_str = ['Артикул;Название;Бренд;Остаток;Резерв;Базовая цена;Валюта;Цена руб. ЦБ;РРЦ руб.' + '\n']
    else:
        list_str = ['Артикул;Название;Бренд;Остаток;Резерв' + '\n']

    workbook = Workbook()
    sheet = workbook.active

    header_style = NamedStyle(name="header")
    header_style.font = Font(bold=True, color=colors.RED, size=12)

    section_style = NamedStyle(name="section")
    section_style.font = Font(bold=True, color=colors.BLUE, size=12)

    sheet.column_dimensions[str(chr(64 + 1))].width = 15
    sheet.column_dimensions[str(chr(64 + 2))].width = 65
    sheet.column_dimensions[str(chr(64 + 3))].width = 15
    sheet.column_dimensions[str(chr(64 + 4))].width = 10
    sheet.column_dimensions[str(chr(64 + 5))].width = 10
    if user:
        sheet.column_dimensions[str(chr(64 + 6))].width = 13
        sheet.column_dimensions[str(chr(64 + 7))].width = 7
        sheet.column_dimensions[str(chr(64 + 8))].width = 13
        sheet.column_dimensions[str(chr(64 + 9))].width = 13

    sheet['A1'] = 'Артикул'
    sheet['B1'] = 'Название'
    sheet['C1'] = 'Бренд'
    sheet['D1'] = 'Остаток'
    sheet['E1'] = 'Резерв'
    if user:
        sheet['F1'] = 'База цена'
        sheet['G1'] = 'Вал.'
        sheet['H1'] = 'Цена руб.'
        sheet['I1'] = 'РРЦ руб.'

    header_row = sheet[1]
    for cell in header_row:
        cell.style = header_style

    row = 2
    for obj_section in sections:

        goods_list = obj_section.get_goods_list_section(user=user, only_stock=True)

        if len(goods_list) > 0:
            sheet[f'A{row}'] = obj_section.name
            sheet[f'A{row}'].style = section_style
            row += 1

        for elem in goods_list:
            code = elem['code'].replace(';', '').replace('"', '')
            name = elem['name'].replace(';', '').replace('"', '')
            brand = elem['brand'].replace(';', '').replace('"', '')
            quantity = str(0 if elem['quantity'] == '' else elem['quantity']).replace('>', '')
            reserve = str(0 if elem['reserve'] == '' else elem['reserve']).replace('>', '')
            price = 0 if elem['price'] == '' else elem['price']
            price_rrp = 0 if elem['price_rrp'] == '' else elem['price_rrp']
            discount = 0 if elem['discount'] == '' else elem['discount']
            currency = 'RUB' if elem['currency'].lower() == 'руб' else elem['currency'].upper()
            course = courses.get(elem['currency_id'], {'course': 1, 'multiplicity': 1})
            price_rub = round(discount * course['course'] / course['multiplicity'], 2)

            # for csv
            if user:
                list_str.append(f'{code};{name};{brand};{quantity};{reserve};{price};{currency};{price_rub};{price_rrp}' + '\n')
            else:
                list_str.append(f'{code};{name};{brand};{quantity};{reserve}' + '\n')

            # for excel
            sheet[f'A{row}'] = code
            sheet[f'B{row}'] = name
            sheet[f'C{row}'] = brand
            sheet[f'D{row}'] = int(quantity)
            sheet[f'E{row}'] = int(reserve)
            if user:
                sheet[f'F{row}'] = price
                sheet[f'G{row}'] = currency
                sheet[f'H{row}'] = price_rub
                sheet[f'I{row}'] = price_rrp
            row += 1

    sheet.title = 'stocks'
    sheet.freeze_panes = 'A2'

    sheet.auto_filter.ref = sheet.dimensions

    # workbook.close()
    workbook.save(filename=path_file_xls)

    with open(path_file_csv, mode='w', encoding='utf-8-sig') as file:
        file.writelines(list_str)

def create_files(user):
    customer = get_customer(user)
    if not customer:
        return
    path_files = os.path.join(settings.BASE_DIR, 'san_site/static/files_for_loading')
    create_directory(path_files)
    path_files_customer = os.path.join(path_files, str(customer.id))
    create_directory(path_files_customer)

    with_reserve = customer.guid in ('9d35a321-ce59-11e6-88f3-20474775d651', '443ca233-ce5a-11e6-88f3-20474775d651',
                                     '3d6cc921-66fb-11ec-bc76-ac1f6bd6c231')

    if with_reserve:
        write_files_with_reserve(path_files_customer, user)
    else:
        write_files(path_files_customer, user)

    url = f'static/{customer.id}/'
    CustomersFiles.objects.filter(customer=customer).delete()

    view = 'Данные в формате CSV (значения разделенные точкой с запятой)'
    CustomersFiles.objects.create(customer=customer,
                                  name='goods_b2b_santex.csv',
                                  view=view,
                                  url=url,
                                  type_file='csv')

    view = 'Данные в формате EXCEL (Microsoft Office Excel)'
    CustomersFiles.objects.create(customer=customer,
                                  name='goods_b2b_santex.xlsx',
                                  view=view,
                                  url=url,
                                  type_file='xlsx')


def create_files_inventories():
    path_files = os.path.join(settings.BASE_DIR, 'san_site/static/files_for_loading')
    create_directory(path_files)
    path_files_customer = os.path.join(path_files, 'inventories')
    create_directory(path_files_customer)
    write_files(path_files_customer)


def create_files_customers():
    # for all
    create_files_inventories()
    # for customers
    customers_yet = []
    users = User.objects.filter(is_active=True)
    for user in users:
        customer = get_customer(user)
        if not customer:
            continue
        if customer.id in customers_yet:
            continue
        create_files(user)
        customers_yet.append(customer.id)
