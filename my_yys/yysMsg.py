# 针对短信记录的特征衍生
from tools.calculate import cal_median
from tools.calculate import division
from tools.calculate import cal_max
from tools.calculate import cal_std
import pandas as pd
import datetime

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

# 中位数和均值相关的衍生
def msg_aver_median(dataObj):
    prefix = 'yysMsg'
    result = dict()
    # 开户时间
    open_date = dataObj.open_data
    # 运营商数据爬取时间
    last_modify_time = dataObj.last_modify_time
    df_smses = dataObj.df_smses
    time_limit_list = []
    time_limit_list.append(last_modify_time)
    for i in (1, 2, 3, 4, 5, 6):
        time_limit_list.append(last_modify_time - datetime.timedelta(days=30 * i))
    every_month_data = []
    for i in range(len(time_limit_list)):
        if (i + 1) < len(time_limit_list):
            temp = df_smses[(df_smses.time > time_limit_list[i + 1]) & (df_smses.time <= time_limit_list[i])]
            every_month_data.append(temp)
    my_dict = [('90d', 90, every_month_data[0: 3]), ('180d', 180, every_month_data)]
    sms_cnt_list = []
    for temp in every_month_data:
        sms_cnt_list.append(temp.shape[0])
    result[f'median_sms_cnt'] = cal_median(sms_cnt_list)
    for md in my_dict:
        msg_cnt_list = []
        msg_send_list = []
        msg_receive_list = []
        msg_fee_list = []
        for temp in md[2]:
            msg_cnt_list.append(temp.shape[0])
            msg_send_list.append(temp[temp.send_type=='SEND'].shape[0])
            msg_receive_list.append(temp[temp.send_type=='RECEIVE'].shape[0])
            msg_fee_list.append(sum(temp['fee'].values))

        if (last_modify_time-datetime.timedelta(md[1]) >= open_date):
            # 月平均短信次数
            result[f'{prefix}_msg_cnt_mean_{md[0]}'] = division(sum(msg_cnt_list), len(msg_cnt_list))
            # 月平均发送次数
            result[f'{prefix}_msg_send_cnt_mean_{md[0]}'] = division(sum(msg_send_list), len(msg_send_list))
            # 月平均接收次数
            result[f'{prefix}_msg_receive_cnt_mean_{md[0]}'] = division(sum(msg_receive_list), len(msg_receive_list))
        else:
            fm = (last_modify_time - open_date)//30 + 1
            # 月平均短信次数
            result[f'{prefix}_msg_cnt_mean_{md[0]}'] = division(sum(msg_cnt_list), fm)
            # 月平均发送次数
            result[f'{prefix}_msg_send_cnt_mean_{md[0]}'] = division(sum(msg_send_list), fm)
            # 月平均接收次数
            result[f'{prefix}_msg_receive_cnt_mean_{md[0]}'] = division(sum(msg_receive_list), fm)
        # 月均最大费用
        result[f'{prefix}_msg_fee_max_month_{md[0]}'] = cal_max(msg_fee_list)
        # 发送次数稳定性
        result[f'{prefix}_msg_send_cnt_month_stab_{md[0]}'] = division(cal_std(msg_send_list), result[f'{prefix}_msg_send_cnt_mean_{md[0]}']) if cal_std(msg_send_list) != '' else ''
        #接收次数稳定性
        result[f'{prefix}_msg_receive_cnt_month_stab_{md[0]}'] = division(cal_std(msg_send_list), result[f'{prefix}_msg_receive_cnt_mean_{md[0]}']) if cal_std(msg_receive_list) != '' else ''
    return result

# 短信记录特征汇总
def yysMsg(dataObj):
    head = 'yysMsg'
    result = dict()
    #cd = cnt_day(dataObj)
    #tid = time_interval_day(dataObj)
    #fcd = fee_contact_day(dataObj)
    mam = msg_aver_median(dataObj)
    #result.update(fcd)
    result.update(mam)
    return result