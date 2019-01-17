import sys
import pymongo
import xlsxwriter

client = pymongo.MongoClient(host='localhost')
db = client['Test']
collection = db.Fargetch_Women_US  # change the correct collection name
cursor = collection.find()
workbook = xlsxwriter.Workbook('FarFetch_Women_US.xlsx')

worksheet = workbook.add_worksheet('Alexander McQueen')
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
worksheet.write(0, 5, 'Original Price', bold)
worksheet.set_column('F:F', 20)
worksheet.write(0, 6, 'Discount', bold)
worksheet.set_column('G:G', 19)
worksheet.write(0, 7, 'Discount Price', bold)
worksheet.set_column('H:H', 20)
worksheet.write(0, 8, 'No. of available sizes', bold)
worksheet.set_column('I:I', 20)
row = 1

current_brand = 'Alexander McQueen'
for one in cursor:
    product_id = one['ID']
    product_name = one['Name']
    product_detail = one['Detail']
    product_price = one['Price']
    product_discount = one['Discount']
    product_sale = one['Sale_price']

    if product_name != current_brand:
        current_brand = product_name
        worksheet = workbook.add_worksheet(product_name)
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
        worksheet.write(0, 5, 'Original Price', bold)
        worksheet.set_column('F:F', 20)
        worksheet.write(0, 6, 'Discount', bold)
        worksheet.set_column('G:G', 19)
        worksheet.write(0, 7, 'Discount Price', bold)
        worksheet.set_column('H:H', 20)
        worksheet.write(0, 8, 'No. of available sizes', bold)
        worksheet.set_column('I:I', 20)
        row = 1

    worksheet.write(row, 0, counter)
    worksheet.write(row, 1, int(product_id))
    worksheet.write(row, 2, product_name)
    worksheet.write(row, 3, product_detail)
    worksheet.write(row, 5, product_price)
    worksheet.write(row, 6, product_discount)
    worksheet.write(row, 7, product_sale)

    bags = ['bag', 'tote', 'backpack', 'pouch']
    shoes = ['boots', 'sneakers', 'sandals', 'flipper']

    try:
        sizes = one['Sizes']
        if sizes == 0:
            worksheet.write(row, 8, 'Size is not needed')
            for b in bags:
                if b in product_detail:
                    worksheet.write(row, 4, 'Bags')
                    break
                else:
                    for sh in shoes:
                        if sh in product_detail:
                            worksheet.write(row, 4, 'Shoes')
                            break
                        else:
                            worksheet.write(row, 4, 'Accessories')
        else:
            worksheet.write(row, 8, sizes)
            for s in shoes:
                if s in product_detail:
                    worksheet.write(row, 4, 'Shoes')
                    break
                else:
                    worksheet.write(row, 4, 'Clothes')
    except Exception as e:
        worksheet.write(row, 8, 'Size is not needed')
        for b in bags:
            if b in product_detail:
                worksheet.write(row, 4, 'Bags')
            else:
                worksheet.write(row, 4, 'Accessories')

    counter += 1
    row += 1

workbook.close()