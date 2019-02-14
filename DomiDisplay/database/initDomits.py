##@package initDomits
# @brief 数据库操作模块
import sqlite3
import pandas

## @fn refactoryDomits(refactoryFilePath,dbpath)
#  @brief 重写domis数据库
#  @param refactoryFilePath 重写需要的文件路径
#  @param dbpath 要重写的数据库路径
#  @return 修改成功返回True
#
#这个函数在用户上传数据库模版文件的时候触发，根据上传的excel文件修改domis.db数据库
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
