##@package initDomits
# @brief 数据库操作模块
import sqlite3
import pandas
from App import app

## @defgroup 数据库操作
#  @brief 包含对数据库的操作
#@{

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

## @fn _tDB(string)
#  @brief 在字符串最外面加上双引号
#  @param string 要加上双引号的字符串
#  @return 加上双引号的string
#  @see searchDB()
#
#  这个函数用来给字符串最外面加上双引号，用于配合数据库查找函数来进行字符串拼接。
def _tDB(string):
    if not string:
        return '"null"'
    else:
        return '"'+string+'"'

## @fn searchDB(db,table,condition="",fetch=-1,cols='*',OrderBy=None,isDesc=False)
#  @brief 数据库查找函数
#  @param condition 给出查找条件，条件中不需要加上WHERE，会自动将这个参数和WHERE语句拼接
#  @param fetch 决定cursor获得多少数据：
#    * 1：执行.fetchone()获取一条数据
#    * >1：执行.fetchmany()获取多条数据
#    * <1：执行.fetchall()获取所有数据
#       默认为-1
#  @param table 要查找的表名
#  @param cols 要匹配的列名，默认为全部匹配
#  @param OrderBy 是否按序查找，默认不按序查找。可以传入按序的列名（只能按照一列）
#  @param isDesc 在按序查找的情况下是否降序查找，默认为False
#  @return 返回查询结果，使用元组返回
#
#  如果db为None，那么函数会通过你给出的参数来进行一次性查询（在内部打开和关闭数据库）。
#  如果db为已经生成的数据库链接，那么查询之后不会关闭数据库。
def searchDB(db, table, condition = "", fetch = -1, cols = '*', OrderBy = None, isDesc = False):
    global flag
    flag = False
    if type(db) == str:
        db = sqlite3.connect(app.config['DATABASE'] + db)
        flag = True
    elif not db:
        return None

    cursor = db.cursor()
    string = 'SELECT %s FROM %s'% (cols,table)
    if not condition == "":
        string += ' WHERE %s' % condition
    if OrderBy:
        string += " ORDER BY %s" % OrderBy
    if isDesc:
        string += " DESC"
    cursor.execute(string)

    global info
    if fetch < 1:
        info = cursor.fetchall()
    elif fetch == 1:
        info = cursor.fetchone()
    else:
        info = cursor.fetchmany(fetch)
    if flag:
        db.close()
    return info

#@}