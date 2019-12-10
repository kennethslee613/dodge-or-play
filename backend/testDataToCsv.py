with open('DB_INFO.txt', 'r') as key:
    DB_INFO = [line.rstrip('\n') for line in key]

connection = pymysql.connect(host=DB_INFO[0],
    port=int(DB_INFO[1]),
    user=DB_INFO[2],
    password=DB_INFO[3],
    db=DB_INFO[4],
    charset='utf8mb4')
cursor = connection.cursor()

query = 'SELECT * FROM testData INTO OUTFILE "testData.csv" FIELDS ENCLOSED BY \'"\' TERMINATED BY ";" ESCAPED BY \'"\' LINES TERMINATED BY "\r\n";'
cursor.execute(query)