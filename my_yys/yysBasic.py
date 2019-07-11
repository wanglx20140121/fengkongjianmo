# 运营商的基础特征的衍生
# author: wen yaxin
# date: 2019/07/09

def yysBasic(dataObj):
    prefix = 'yysBasic'
    result = dict()
    # 用户手机号
    result[f'{prefix}_mobile'] = dataObj.mobile
    # 用户手机号码归属地
    result[f'{prefix}_attribution'] = dataObj.attribution
    # 数据爬取时间
    result[f'{prefix}_last_modify_time'] = dataObj.last_modify_time
    result[f'{prefix}_open_data'] = (dataObj.last_modify_time - dataObj.open_data).days
    result[f'{prefix}_star_level'] = dataObj.star_level
    return result
