# 充值记录的特征衍生
from tools.calculate import cal_max
from tools.calculate import cal_min
from tools.calculate import division
from tools.calculate import cal_median
from tools.calculate import cal_std
import datetime

# 充值次数 + 时间衍生， 充值金额 + 时间衍生
def fee_cnt_time(dataObj):
    prefix = 'yysRecharge'
    result = dict()
    last_modify_time = dataObj.last_modify_time
    df_recharges = dataObj.df_recharges
    day_list = []
    array = (30, 90, 180)
    amount_cut = [10, 20, 50, 100, 150, 200]
    for i in array:
        x = (str(i) + 'd', df_recharges[(last_modify_time - df_recharges['recharge_time']).dt.days <= i])
        day_list.append(x)
    for day in day_list:
        temp = day[1][['recharge_time', 'amount']]
        # 近x天充值总金额
        result[f'{prefix}_sum_recharge_amout_{day[0]}'] = sum(temp['amount'].values)
        # 近x天充值次数
        result[f'{prefix}_recharge_cnt_sum_{day[0]}'] = temp.shape[0]
        # 近x天单笔充值金额中位数
        result[f'{prefix}_recharge_amount_median_{day[0]}'] = cal_median(temp['amount'].values)
        # 近x天单笔充值金额最大值
        result[f'{prefix}_recharge_amount_max_{day[0]}'] = cal_max(temp['amount'].values)
        # 近x天充值费用平均值，按笔算
        result[f'{prefix}_recharge_amount_mean_{day[0]}_fm_cnt'] = division(sum(temp['amount'].values), temp.shape[0])

        for ac in amount_cut:
            amount = 10*ac
            match_df = temp[temp.amount > 10*ac]
            result[f'{prefix}_recharge_amount{amount}_cnt_{day[0]}'] = match_df.shape[0]

        if day[0]=='90d' or day[0]=='180d':
            array = []
            match_df = sorted(temp['recharge_time'])
            for i in range(0, len(match_df)):
                if (i+1) < len(match_df):
                    day_dis = (match_df[i+1]-match_df[i]).days
                    array.append(day_dis)
            # 近x天相邻两笔充值最大间隔
            result[f'{prefix}_recharge_timespan_max_{day[0]}'] = cal_max(array)
            # 近x天相邻两笔充值最小间隔
            result[f'{prefix}_recharge_timespan_min_{day[0]}'] = cal_min(array)
            # 近x天相邻两笔充值间隔均值
            result[f'{prefix}_recharge_timespan_mean_{day[0]}'] = division(sum(array), len(array))

    recharge_time = sorted(df_recharges['recharge_time'])
    # 最近一次充值距更新时间天数
    result[f'{prefix}_trade_recent_time_span'] = (last_modify_time - recharge_time[len(recharge_time) - 1]).days
    print('recharge fee cnt time count:', len(result))
    return result



# 针对中位数和均值的衍生
def recharge_aver_median(dataObj):
    prefix = 'yysRecharge'
    result = dict()
    open_date = dataObj.open_data
    last_modify_time = dataObj.last_modify_time
    df_recharge = dataObj.df_recharges
    time_limit_list = []
    time_limit_list.append(last_modify_time)
    for i in (1, 2, 3, 4, 5, 6):
        time_limit_list.append(last_modify_time - datetime.timedelta(days=30 * i))
    every_month_data = []
    for i in range(len(time_limit_list)):
        if (i + 1) < len(time_limit_list):
            temp = df_recharge[(df_recharge.time > time_limit_list[i + 1]) & (df_recharge.time <= time_limit_list[i])]
            every_month_data.append(temp)
    my_dict = [('90d', 90, every_month_data[0: 3]), ('180d', 180, every_month_data)]
    recharge_cnt = []
    for temp in every_month_data:
        recharge_cnt.append(temp.shape[0])
    result[f'{prefix}_rechange_cnt_median'] = cal_median(recharge_cnt)
    for md in my_dict:
        recharge_cnt_list = []     # 存放月充值次数
        recharge_amount_list = []  # 存放月充值金额
        for temp in md[2]:
            recharge_cnt_list.append(temp.shape[0])
            recharge_amount_list.append(sum(temp['amount'].values))
        if (last_modify_time - datetime.timedelta(md[1]) >= open_date):
            # 月均费用平均值
            result[f'{prefix}_recharge_amount_mean_{md[0]}_fm_month'] = division(sum(recharge_amount_list), len(recharge_amount_list))
            # 月均充值次数
            result[f'{prefix}_recharge_cnt_mean_{md[0]}'] = division(sum(recharge_cnt_list), len(recharge_cnt_list))
        else:
            fm =  fm = (last_modify_time - open_date)//30 + 1
            # 月均费用平均值
            result[f'{prefix}_recharge_amount_mean_{md[0]}_fm_month'] = division(sum(recharge_amount_list), fm)
            # 月均充值次数
            result[f'{prefix}_recharge_cnt_mean_{md[0]}'] = division(sum(recharge_cnt_list), fm)
        # 月均充值次数最大值
        result[f'{prefix}_recharge_cnt_max_{md[0]}'] = cal_max(recharge_cnt_list)
        # 月均充值金额最大值
        result[f'{prefix}_recharge_amount_month_max_{md[0]}'] = cal_max(recharge_amount_list)
        # 月均充值次数稳定性
        result[f'{prefix}_recharge_cnt_month_stab_{md[0]}'] = division(cal_std(recharge_cnt_list), result[f'{prefix}_recharge_cnt_mean_{md[0]}_fm_month']) if cal_std(recharge_cnt_list) != '' else ''
        # 月均充值金额稳定性
        result[f'{prefix}_recharge_cnt_month_stab_{md[0]}'] = division(cal_std(recharge_amount_list), result[f'{prefix}_recharge_amount_mean_{md[0]}_fm_month']) if cal_std(recharge_amount_list) != '' else ''

    print('yysRecharge recharge aver median feature count:', len(result))
    return result


# 充值记录的特征衍生
def yysRecharge(dataObj):
    prefix = 'yysRecharge'
    result = dict()
    #fct = fee_cnt_time(dataObj)
    ram = recharge_aver_median(dataObj)
    #result.update(fct)
    result.update(ram)
    return result
