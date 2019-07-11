# 账单特征衍生
from tools.calculate import cal_max
from tools.calculate import cal_min
from tools.calculate import division
from tools.calculate import cal_median


# 账单费用 + 时间轴衍生
def fee_time(dataObj):
    prefix = 'yysBill'
    result = dict()
    last_modify_time = dataObj.last_modify_time
    df_bill = dataObj.df_bills
    # 近6个月各种费用平均值
    result[f'{prefix}_bill_total_fee_month_mean'] = df_bill.total_fee.mean()
    result[f'{prefix}_bill_actual_fee_month_mean'] = df_bill.actual_fee.mean()
    result[f'{prefix}_bill_voice_fee_month_mean'] = df_bill.voice_fee.mean()
    result[f'{prefix}_bill_extra_service_fee_month_mean'] = df_bill.extra_service_fee.mean()
    result[f'{prefix}_bill_sms_fee_month_mean'] = df_bill.sms_fee.mean()
    result[f'{prefix}_bill_extra_fee_month_mean'] = df_bill.extra_fee.mean()
    result[f'{prefix}_bill_web_fee_month_mean'] = df_bill.web_fee.mean()
    # 近6个月各种费用中位数
    result[f'{prefix}_bill_total_fee_month_mean'] = df_bill.total_fee.median()
    result[f'{prefix}_bill_actual_fee_month_mean'] = df_bill.actual_fee.median()
    result[f'{prefix}_bill_voice_fee_month_mean'] = df_bill.voice_fee.median()
    result[f'{prefix}_bill_extra_service_fee_month_mean'] = df_bill.extra_service_fee.median()
    result[f'{prefix}_bill_sms_fee_month_mean'] = df_bill.sms_fee.median()
    result[f'{prefix}_bill_extra_fee_month_mean'] = df_bill.extra_fee.median()
    result[f'{prefix}_bill_web_fee_month_mean'] = df_bill.web_fee.median()

    my_dict = {3:'', 6:''}
    year = last_modify_time.year
    month = last_modify_time.month
    for i in (3,6):
        if (month-i)>0:
            month_threshold = month - i
            year_threshold = year
        else:
            month_threshold = month + 12 - i
            year_threshold = year - 1
        month_year_df = df_bill[((df_bill.bill_month).dt.year>=year_threshold)&((df_bill.bill_month).dt.month>=month_threshold)]
        if i == 3:
            my_dict[3] = month_year_df
        if i == 6:
            my_dict[6] = month_year_df
    day_list = {(3, '90d'), (6, '180d')}
    fee_list = [10, 20, 50, 100, 150, 200]

    for md in my_dict:
        print(f'---------{md[0]}----------')
        print(md[1])

    for day in day_list:
        df_temple = my_dict[day[0]]
        # 费用之和
        if day[0] >= df_temple.shape[0]:
            # 总费用
            result[f'{prefix}_bill_total_fee_sum_{day[1]}'] = df_temple.total_fee.sum()
            # 实际费用
            result[f'{prefix}_bill_actual_fee_sum_{day[1]}'] = df_temple.actual_fee.sum()
            # 语音费用
            result[f'{prefix}_bill_voice_fee_sum_{day[1]}'] = df_temple.voice_fee.sum()
            # 语音费用占比
            result[f'{prefix}_bill_voice_fee_sum_rate_{day[1]}'] = division(df_temple.voice_fee.sum(), df_temple.total_fee.sum())
            # 其他费用
            result[f'{prefix}_bill_extra_service_fee_sum_{day[1]}'] = df_temple.extra_service_fee.sum()
            # 其他费用占比
            result[f'{prefix}_bill_extra_service_fee_sum_rate_{day[1]}'] = division(df_temple.extra_service_fee.sum(), df_temple.total_fee.sum())
            # 短信费用
            result[f'{prefix}_bill_sms_fee_sum_{day[1]}'] = df_temple.sms_fee.sum()
            # 短信费用占比
            result[f'{prefix}_bill_sms_fee_sum_rate_{day[1]}'] = division(df_temple.sms_fee.sum(), df_temple.total_fee.sum())
            result[f'{prefix}_bill_extra_fee_sum_{day[1]}'] = df_temple.extra_fee.sum()
            result[f'{prefix}_bill_extra_fee_sum_rate_{day[1]}'] = division(df_temple.extra_fee.sum(), df_temple.total_fee.sum())
            result[f'{prefix}_bill_web_fee_sum_{day[1]}'] = df_temple.web_fee.sum()
            result[f'{prefix}_bill_web_fee_sum_rate_{day[1]}'] = division(df_temple.web_fee.sum(), df_temple.total_fee.sum())
        else:
            df1 = df_temple.iloc[:day[0]]
            result[f'{prefix}_bill_total_fee_sum_{day[1]}'] = df1.total_fee.sum()
            result[f'{prefix}_bill_actual_fee_sum_{day[1]}'] = df1.actual_fee.sum()
            result[f'{prefix}_bill_voice_fee_sum_{day[1]}'] = df1.voice_fee.sum()
            result[f'{prefix}_bill_voice_fee_sum_rate_{day[1]}'] = division(df1.voice_fee.sum(), df1.total_fee.sum())
            result[f'{prefix}_bill_extra_service_fee_sum_{day[1]}'] = df1.extra_service_fee.sum()
            result[f'{prefix}_bill_extra_service_fee_sum_rate_{day[1]}'] = division(df1.extra_service_fee.sum(), df1.total_fee.sum())
            result[f'{prefix}_bill_sms_fee_sum_{day[1]}'] = df1.sms_fee.sum()
            result[f'{prefix}_bill_sms_fee_sum_rate_{day[1]}'] = division(df1.sms_fee.sum(), df1.total_fee.sum())
            result[f'{prefix}_bill_extra_fee_sum_{day[1]}'] = df1.extra_fee.sum()
            result[f'{prefix}_bill_extra_fee_sum_rate_{day[1]}'] = division(df1.extra_fee.sum(), df1.total_fee.sum())
            result[f'{prefix}_bill_web_fee_sum_{day[1]}'] = df1.web_fee.sum(df1.web_fee.sum(), df1.total_fee.sum())
        # 费用最值
        result[f'{prefix}_bill_total_fee_month_max_{day[1]}'] = cal_max(df_temple.total_fee.values)
        result[f'{prefix}_bill_actual_fee_month_max_{day[1]}'] = cal_max(df_temple.actual_fee.values)
        result[f'{prefix}_bill_voice_fee_month_max_{day[1]}'] = cal_max(df_temple.voice_fee.values)
        result[f'{prefix}_bill_extra_service_fee_month_max_{day[1]}'] = cal_max(df_temple.extra_service_fee.values)
        result[f'{prefix}_bill_sms_fee_month_max_{day[1]}'] = cal_max(df_temple.sms_fee.values)
        result[f'{prefix}_bill_extra_fee_month_max_{day[1]}'] = cal_max(df_temple.extra_fee.values)
        result[f'{prefix}_bill_web_fee_month_max_{day[1]}'] = cal_max(df_temple.web_fee.values)

        for fee in fee_list:
            temp_total = df_temple[['bill_month', 'total_fee', 'web_fee']][df_temple.total_fee > (fee * 100)]
            temp_web = df_temple[['bill_month', 'total_fee', 'web_fee']][df_temple.web_fee > (fee * 100)]
            result[f'{prefix}_bill_totalfee{fee}_cnt_{day[1]}'] = min(temp_total.shape[0], day[0])
            result[f'{prefix}_bill_webfee{fee}_cnt_{day[1]}'] = min(temp_web.shape[0], day[0])

    print('fee time feature count:', len(result))
    return result


def yysBill(dataObj):
    prefix = 'yysBill'
    result = dict()
    ft = fee_time(dataObj)
    result.update(ft)
    return result
