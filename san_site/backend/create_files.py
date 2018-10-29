from san_site.models import get_customer, Section, Currency, CustomersFiles
from django.contrib.auth.models import User
from django.conf import settings
import xlsxwriter
import os


def create_directory(path):
    if os.path.exists(path) and not os.path.isdir(path):
        print(f'Error: {path} - is not a directory')
        os.remove(path)
        print(f'Error: file with name {path} - was remove')
    if not os.path.exists(path):
        os.mkdir(path)
        print(f'Information: Directory with name {path} - was created')


def write_files(user, path_files_customer):

    courses = {}
    currency = Currency.objects.all()
    for elem in currency:
        courses[elem.id] = elem.get_today_course()

    path_file_csv = os.path.join(path_files_customer, 'goods_b2b_santex.csv')
    path_file_xls = os.path.join(path_files_customer, 'goods_b2b_santex.xlsx')
    sections = Section.objects.filter(parent_guid='---')

    if os.path.exists(path_file_xls):
        os.remove(path_file_xls)

    list_str = ['code;name;quantity;price_rub' + '\n']

    workbook = xlsxwriter.Workbook(path_file_xls, {'constant_memory': True})
    worksheet = workbook.add_worksheet()

    row = 0
    for obj_section in sections:
        goods_list = obj_section.get_goods_list_section(user=user, only_stock=True)
        for elem in goods_list:
            code = elem['code'].replace(';', '').replace('"', '')
            name = elem['name'].replace(';', '').replace('"', '')
            quantity = str(0 if elem['quantity'] == '' else elem['quantity']).replace('>', '')
            price = 0 if elem['discount'] == '' else elem['discount']
            course = courses.get(elem['currency_id'], {'course': 1, 'multiplicity': 1})
            price_rub = round(price * course['course'] / course['multiplicity'], 2)

            # for csv
            list_str.append(f'{code};{name};{quantity};{price_rub}' + '\n')

            # for excel
            worksheet.write(row, 0, code)
            worksheet.write(row, 1, name)
            worksheet.write(row, 2, int(quantity))
            worksheet.write(row, 3, price_rub)
            row += 1

    workbook.close()

    with open(path_file_csv, mode='w', encoding='utf-8-sig') as file:
        file.writelines(list_str)


def create_files(user):
    customer = get_customer(user)
    if not customer:
        return
    path_files = os.path.join(settings.BASE_DIR, 'san_site\\static\\files_for_loading')
    create_directory(path_files)
    path_files_customer = os.path.join(path_files, str(customer.id))
    create_directory(path_files_customer)

    write_files(user, path_files_customer)

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
                                  type_file='exlx')


def create_files_customers():
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
