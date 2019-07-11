# 充值记录的特征衍生
from tools.calculate import cal_max
from tools.calculate import cal_min
from tools.calculate import division
from tools.calculate import cal_median

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
        result[f'recharge_amount_max_{day[0]}'] = cal_max(temp['amount'].values)
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



# 充值记录的特征衍生
def yysRecharge(dataObj):
    prefix = 'yysRecharge'
    result = dict()
    fct = fee_cnt_time(dataObj)
    result.update(fct)
    return result
