import sqlite3
import pandas

def refactoryDomits(refactoryFilePath,dbpath):
    db = sqlite3.connect(dbpath+'domis.db')
    cursor = db.cursor()
    df = pandas.read_excel(refactoryFilePath)
    for i in range(len(df)):
        command = 'INSERT OR REPLACE INTO domits(name,score) VALUES(%s,%d)' % ('"' + df.iloc[i]['宿舍'] + '"',int(df.iloc[i]['分数']))
        cursor.execute(command)
        db.commit()
    db.close()
    return True