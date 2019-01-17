import sys
import pymongo
import xlsxwriter

client = pymongo.MongoClient(host='localhost')
db = client['Test']
collection = db.Net_A_Porter  # change the correct collection name
cursor = collection.find()
workbook = xlsxwriter.Workbook('Net_A_Porter.xlsx')

worksheet = workbook.add_worksheet('Alexander McQueen')
sheets = ['Alexander McQueen']
bold = workbook.add_format({'bold': True})
worksheet.write(0, 0, '#', bold)
counter = 1
worksheet.write(0, 1, 'Store ID', bold)
worksheet.set_column('B:B', 12)
worksheet.write(0, 2, 'Brand', bold)
worksheet.set_column('C:C', 20)
worksheet.write(0, 3, 'Description', bold)
worksheet.set_column('D:D', 20)
worksheet.write(0, 4, 'Category', bold)
worksheet.set_column('E:E', 19)
worksheet.write(0, 5, 'Original Price(USD)', bold)
worksheet.set_column('F:F', 20)
worksheet.write(0, 6, 'Discount', bold)
worksheet.set_column('G:G', 19)
worksheet.write(0, 7, 'Discount Price(USD)', bold)
worksheet.set_column('H:H', 20)
worksheet.write(0, 8, 'No. of available sizes', bold)
worksheet.set_column('I:I', 20)
row = 1

current_brand = 'Alexander McQueen'
for one in cursor:
    product_id = one['ID']
    product_cate = one['Category']
    product_name = one['Name']
    product_detail = one['Detail']
    product_price = one['Price']
    product_discount = one['Discount']
    product_sale = one['Sale_price']
    product_sizes = one['Sizes']

    if product_name != current_brand:
        if product_name not in sheets:
            sheets.append(product_name)
            current_brand = product_name
            worksheet = workbook.add_worksheet(product_name)
        else:
            worksheet = workbook.get_worksheet_by_name(product_name)

        worksheet.write(0, 0, '#', bold)
        counter = 1
        worksheet.write(0, 1, 'Store ID', bold)
        worksheet.set_column('B:B', 12)
        worksheet.write(0, 2, 'Brand', bold)
        worksheet.set_column('C:C', 20)
        worksheet.write(0, 3, 'Description', bold)
        worksheet.set_column('D:D', 20)
        worksheet.write(0, 4, 'Category', bold)
        worksheet.set_column('E:E', 19)
        worksheet.write(0, 5, 'Original Price(USD)', bold)
        worksheet.set_column('F:F', 20)
        worksheet.write(0, 6, 'Discount', bold)
        worksheet.set_column('G:G', 19)
        worksheet.write(0, 7, 'Discount Price(USD)', bold)
        worksheet.set_column('H:H', 20)
        worksheet.write(0, 8, 'No. of available sizes', bold)
        worksheet.set_column('I:I', 20)
        row = 1

    worksheet.write(row, 0, counter)
    worksheet.write(row, 1, int(product_id))
    worksheet.write(row, 2, product_name)
    worksheet.write(row, 3, product_detail)
    worksheet.write(row, 4, product_cate)
    worksheet.write(row, 5, product_price)
    worksheet.write(row, 6, product_discount)
    worksheet.write(row, 7, product_sale)
    if product_sizes == 0:
        worksheet.write(row, 8, 'Size is not needed')
    else:
        worksheet.write(row, 8, product_sizes)
    counter += 1
    row += 1

workbook.close()