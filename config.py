# 安全参数
SECRET_KEY = "f268fb9f508111eaaa87c75bfedfb617503e3a6126524682a5598d0c08ec1da1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

LZ_DB_MYSQL_CONFIG = dict(
    url='mysql://jenifly:jyzzjwdlz^6@localhost:3306/zjlzgl',
    min_size=5,
    max_size=10
)
# 主程序数据数据库 MySQL

LZ_DB_REDIS_CONFIG = dict(
    address=('localhost', 6379),
    password='rdjenifly0.1'
)
# 主程序缓存数据库 Redis

# 人员表字典
USER_DICT = {
    '工资号': 'id',
    '姓名': 'name',
    '简拼码': 'simple',
    '性别': 'sex',
    '手机号': 'phone',
    '部门': 'dp',
    '原部门': 'dp_',
    '职名': 'position',
    '原职名': 'position_',
    '组别': 'group',
    '身份证号': 'identity',
    '工作证号': 'work_id',
    '入职年月': 'work_date',
    '学历': 'education',
    '毕业院校': 'graduate',
    '专业': 'specific',
    '政治面貌': 'politics_status',
    '籍贯': 'native',
    '民族': 'nation',
    '地址': 'address'
}
