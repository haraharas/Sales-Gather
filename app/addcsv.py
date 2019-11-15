# addCsv.py
from django.db import connection
import logging
import csv
from datetime import datetime as dt
logger = logging.getLogger('development')
# DBへの追加用SQL
sql_insert = ("insert into app_sale (store,sale_date,sale,cost, created_at) "
              "select * from (select %s as store, %s as sale_date, %s as sale, %s as cost, "
              "%s as created_at) as tmp")


def regist_data(cursor, file_path):
    # ファイル読み込み（CSV形式）
    try:
        file = open(file_path, newline='')
    except IOError:
        logger.warning('対象ファイルが存在しません：' + file_path)
        logger.warning('DB登録は行いません：' + file_path)
    else:
        logger.info('=== > Start DB登録 ==')
        with file:
            reader = csv.reader(file)
            header = next(reader)  # ヘッダーをスキップ
            for row in reader:
                str_time = [dt.now().strftime('%Y-%m-%d %H:%M:%S')]
                add_data = []
                add_data.extend(row)  # csvから読み取った情報
                add_data.extend(str_time)  # created_at
                add_data.append(row[3])  # ロケーションID（対象レコードがDBに存在するかの確認に使用する）
                add_data.append(row[0])  # 対象日時（対象レコードがDBに存在するかの確認に使用する）
                logger.debug('add_data = ' + str(add_data))
                # レコード追加
                cursor.execute(sql_insert, add_data)
            logger.info("=== > End DB登録 ==")
# csvファイルのデータをDBに追加する。


def insert_csv_data(file_path):
    logger.info('== csvデータ登録処理開始 ==')
    with connection.cursor() as cursor:
        regist_data(cursor, file_path)
    logger.info('== csvデータ登録処理終了 ==')
