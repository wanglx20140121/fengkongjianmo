# 针对短信记录的特征衍生
from tools.calculate import cal_median
from tools.calculate import division
from tools.calculate import cal_max
import pandas as pd

# 基于时间轴对短信次数衍生
def cnt_day(dataObj):
    prefix = 'yysMsg'
    result = dict()
    last_modify_time = dataObj.last_modify_time
    df_smses = dataObj.df_smses
    day_list = []
    array = (3, 7, 15, 30, 90, 180)
    for i in array:
        x = (str(i)+'d', df_smses[(last_modify_time - df_smses['time']).dt.days <= i])
        day_list.append(x)
    for day in day_list:
        temp = day[1]
        # 近x天短信次数
        result[f'{prefix}_sum_msg_cnt_{day[0]}'] = temp.shape[0]
        if day[0]=='30d' or day[0]=='90d' or day[0]=='180d':
            # 近x个月短信发送次数
            result[f'{prefix}_msg_send_cnt_sum_{day[0]}'] = [temp[temp.send_type == 'SEND'].shape[0]]
            # 近x个月短信接收次数
            result[f'{prefix}_msg_receive_cnt_sum_{day[0]}'] = [temp[temp.send_type == 'RECEIVE'].shape[0]]
    print('msg cnt day feature count:', len(result))
    return result


# 发送时段 + 发送方式 + 时间段衍生
def time_interval_day(dataObj):
    prefix = 'yysMsg'
    result = dict()
    last_modify_time = dataObj.last_modify_time
    df_smses = dataObj.df_smses
    day_list = []
    array = (30, 90, 180)
    for i in array:
        x = (str(i) + 'd', df_smses[(last_modify_time - df_smses['time']).dt.days <= i])
        day_list.append(x)
    time_interval_list = [('morning', 6, 12),('afternoon', 12, 18), ('evening', 18, 24), ('midnight', 0, 6)]
    for day in day_list:
        data = day[1][['time','send_type']]
        temp = data.copy()
        temp = data['time'].dt.hour
        for ti in time_interval_list:
            # 近x天通话时段在(y,z]内的短信记录
            match_df = temp[(temp.hour > ti[1]) & (temp.hour <= ti[2])]
            # 近x月tr[1]-tr[2]时段的短信发送次数
            result[f'{prefix}_msg_send_cnt_{ti[0]}_sum_{day[0]}'] = match_df[match_df.send_type == 'SEND'].shape[0]
            # 近x月tr[1]-tr[2]时段的短信接收次数
            result[f'{prefix}_msg_receive_cnt_{ti[0]}_sum_{day[0]}'] = match_df[match_df.send_type == 'RECEIVE'].shape[0]
    print('msg time interval day feature count:', len(result))
    return result

# 短信费用 + 时间轴衍生, 联系次数 + 时间轴衍生
def fee_contact_day(dataObj):
    prefix = 'yysMsg'
    result = dict()
    last_modify_time = dataObj.last_modify_time
    df_smses = dataObj.df_smses
    day_list = []
    array = (30, 90, 180)
    for i in array:
        x = (str(i) + 'd', df_smses[(last_modify_time - df_smses['time']).dt.days <= i])
        day_list.append(x)

    for day in day_list:
        temp = day[1][['peer_number', 'fee', 'time']]
        # 近x天短信费用
        result[f'{prefix}_msg_fee_sum_{day[0]}'] = sum(temp['fee'].values)
        # 近x天短信最大费用
        result[f'{prefix}_msg_fee_max_day_{day[0]}'] = cal_max(temp['fee'].values)
        number_cnt = temp['peer_number'].value_counts()
        number_cnt = number_cnt.reset_index()
        # 近x个月短信次数超过2,5,10的联系人个数
        result[f'{prefix}_msg_cnt2_num_{day[0]}'] = len(set(number_cnt['index'][number_cnt.peer_number > 2]))
        result[f'{prefix}_msg_cnt5_num_{day[0]}'] = len(set(number_cnt['index'][number_cnt.peer_number > 5]))
        result[f'{prefix}_msg_cnt10_num_{day[0]}'] = len(set(number_cnt['index'][number_cnt.peer_number > 10]))

    temp = df_smses.copy()
    temp['year'] = df_smses['time'].dt.year
    temp['month'] = df_smses['time'].dt.month
    temp = temp.groupby(['year', 'month'])
    sum_fee_list = []
    for index,data in temp:
        sum_fee_list.append(sum(data['fee'].values))
    result[f'{prefix}_msg_fee10_cnt_{day[0]}'] = len([x for x in sum_fee_list if x > 10])
    result[f'{prefix}_msg_fee50_cnt_{day[0]}'] = len([x for x in sum_fee_list if x > 50])
    print('msg fee day feature count:', len(result))
    return result



# 短信记录特征汇总
def yysMsg(dataObj):
    head = 'yysMsg'
    result = dict()
    #cd = cnt_day(dataObj)
    #tid = time_interval_day(dataObj)
    fcd = fee_contact_day(dataObj)
    result.update(fcd)
    return result