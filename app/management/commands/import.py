from django.core.management.base import BaseCommand, CommandError
from ...models import Sale
import csv
import io
import os
from datetime import datetime
UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + '/csv/'
csv_name = ['oroshi.csv', 'kakou.csv', 'etc.csv']


class Command(BaseCommand):

    def handle(self, *args, **options):
        # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
        for cn in csv_name:
            path = os.path.join(UPLOAD_DIR, cn)
            if os.path.exists(path):
                with open(path) as csvfile:
                    reader = csv.reader(csvfile)
                    dt_time = datetime.now()
                    # 1行ずつ取り出し、作成していく
                    for row in reader:
                        sale, created = Sale.objects.get_or_create(
                            store=row[0], sale_date=row[1], csv_import=True, defaults=dict(
                                store=row[0], sale=row[2], cost=row[3], created_at=dt_time)
                        )
                        sale.store = row[0]
                        sale.sale_date = row[1]
                        if int(row[2]) != 0:
                            sale.sale = row[2]
                        if int(row[3]) != 0:
                            sale.cost = row[3]
                        sale.csv_import = True
                        sale.save()
            os.remove(path)
