from tools.calculate import cal_median
from tools.calculate import division
from tools.calculate import cal_max
import pandas as pd
import datetime
# 针对运营商通话记录的衍生


# 针对通话时长和天数的衍生
def duration_day(dataObj):
    prefix = 'yysCall'
    result = dict()
    last_modify_time = dataObj.last_modify_time
    # 通话时长区间，单位s, 取左开右闭
    duration_list = [(0,30), (30,60), (60,180), (180,300), (300,600), (600, 'up')]
    df_callRecord_3day = dataObj.df_callRecord[(last_modify_time - dataObj.df_callRecord['time']).dt.days <= 3]
    df_callRecord_15day = dataObj.df_callRecord[(last_modify_time - dataObj.df_callRecord['time']).dt.days <= 15]
    day_list = [
        ('3d', df_callRecord_3day),
        ('7d', dataObj.df_callRecord_7day),
        ('15d',df_callRecord_15day),
        ('30d', dataObj.df_callRecord_1m),
        ('90d', dataObj.df_callRecord_3m),
        ('180d', dataObj.df_callRecord)
    ]
    for day in day_list:
        # temp是近x天的通话记录
        temp = day[1]
        # 近x天互通联系人个数
        result[f'{prefix}_dial_dialed_contacter_cnt_{day[0]}'] = len(set(temp['peer_number'][temp.dial_type == 'DIAL'].values) & set(temp['peer_number'][temp.dial_type == 'DIALED'].values))
        # 近x天联系人数量
        result[f'{prefix}_contacter_cnt_{day[0]}'] = len(set(temp['peer_number']))
        # 近x天通话次数
        result[f'{prefix}_call_cnt_{day[0]}'] = temp.shape[0]
        # 近x天主叫次数
        result[f'{prefix}_dial_cnt_{day[0]}'] = temp['peer_number'][temp.dial_type == 'DIAL'].shape[0]
        # 近x天被叫次数
        result[f'{prefix}_dialed_cnt_{day[0]}'] = temp['peer_number'][temp.dial_type == 'DIALED'].shape[0]
        # 近x天通话时长总和
        result[f'{prefix}_call_time_{day[0]}'] = sum(temp['duration'].values)
        # 近x天主叫时长总和
        result[f'{prefix}_dial_time_{day[0]}'] = sum(temp['duration'][temp.dial_type == 'DIAL'].values)
        # 近x天被叫时长总和
        result[f'{prefix}_dialed_time_{day[0]}'] = sum(temp['duration'][temp.dial_type == 'DIALED'].values)
        # 近x天被叫时长中位数
        result[f'{prefix}_dialed_time_median_{day[0]}'] = cal_median(temp['duration'][temp.dial_type == 'DIALED'].values.tolist())
        # 近x天主叫时长中位数
        result[f'{prefix}_dial_time_median_{day[0]}'] = cal_median(temp['duration'][temp.dial_type == 'DIAL'].values.tolist())
        # 近x天最大通话时长
        result[f'{prefix}_call_max_time_{day[0]}'] = cal_max(temp['duration'].values)
        # 近x天主叫最大通话时长
        result[f'{prefix}_dial_max_time_{day[0]}'] = cal_max(temp['duration'][temp.dial_type=='DIAL'].values)
        # 近x天被叫最大通话时长
        result[f'{prefix}_dialed_max_time_{day[0]}'] = cal_max(temp['duration'][temp.dial_type=='DIAL'].values)

        for dr in duration_list:
            # match是近x天通话时长在(y,z]秒的记录, match_df是符合筛选条件的记录
            if dr[1] == 'up':
                match_df = temp[['peer_number','dial_type','duration']][temp.duration > dr[0]]
            else:
                match_df = temp[['peer_number','dial_type','duration']][(temp.duration > dr[0]) & (temp.duration <= dr[1])]
            # 近x天通话时长(y,z]秒内的通话记录的通话总时长
            result[f'{prefix}_duration_{dr[0]}_{dr[1]}_sum_{day[0]}'] = sum(match_df['duration'].values.tolist())
            # 近x天主叫时长(y,z]秒内的通话记录的通话总时长
            result[f'{prefix}_dial_duration_{dr[0]}_{dr[1]}_sum_{day[0]}'] = sum(match_df['duration'][match_df.dial_type == 'DIAL'].values)
            # 近x天被叫时长(y,z]秒内的通话记录的通话总时长
            result[f'{prefix}_dialed_duration_{dr[0]}_{dr[1]}_sum_{day[0]}'] = sum(match_df['duration'][match_df.dial_type == 'DIALED'].values)
            # 近x天通话时长(y,z]秒内的联系人个数
            result[f'{prefix}_contacter_{dr[0]}_{dr[1]}_cnt_{day[0]}'] = len(set(match_df['peer_number'].values))
            # 近x天通话时长(y,z]秒内互通联系人个数
            result[f'{prefix}_dial_dialed_contacter_{dr[0]}_{dr[1]}_cnt_{day[0]}'] = len(set(match_df['peer_number'][match_df.dial_type == 'DIAL'].values.tolist()) & set(match_df['peer_number'][match_df.dial_type == 'DIALED'].values.tolist()))
            # 近x天通话时长(y,z)秒内的联系人个数占比
            result[f'{prefix}_contacter_{dr[0]}_{dr[1]}_rate_{day[0]}'] = division(result[f'{prefix}_contacter_{dr[0]}_{dr[1]}_cnt_{day[0]}'],len(set(temp['peer_number'].values)))
            # 近x天主叫联系人 和 被叫联系人
            dial_number = set(temp['peer_number'][temp.dial_type == 'DIALED'].values.tolist())
            dialed_number = set(temp['peer_number'][temp.dial_type == 'DIAL'].values.tolist())
            # 近x天通话时长在(y,z]秒内互通联系人个数占比
            result[f'{prefix}_dial_dialed_contacter_{dr[0]}_{dr[1]}_rate_{day[0]}'] = division(result[f'{prefix}_dial_dialed_contacter_{dr[0]}_{dr[1]}_cnt_{day[0]}'], len(dial_number & dialed_number))
            # 近x天通话时长在(y,z]秒内的通话次数
            result[f'{prefix}_call_{dr[0]}_{dr[1]}_cnt_{day[0]}'] = match_df.shape[0]
            # 近x天通话时长在(y,z]秒内的通话次数占比
            result[f'{prefix}_call_{dr[0]}_{dr[1]}_rate_{day[0]}'] = division(match_df.shape[0], temp.shape[0])
            # 近x天通话时长在(y,z]秒内的主叫通话次数
            result[f'{prefix}_caller_{dr[0]}_{dr[1]}_cnt_{day[0]}'] = match_df['peer_number'][match_df.dial_type == 'DIAL'].shape[0]
            # 近x天通话时长在(y,z]秒内的被叫通话次数
            result[f'{prefix}_called_{dr[0]}_{dr[1]}_cnt_{day[0]}'] = match_df['peer_number'][match_df.dial_type == 'DIALED'].shape[0]
            # 近x天通话时长在(y,z]秒的主叫号码数
            calling = match_df['peer_number'][match_df.dial_type == 'DIAL'].values.tolist()
            called = match_df['peer_number'][match_df.dial_type == 'DIALED'].values.tolist()
            # 近x月通话时长在(y,z]秒的互相通话次数
            result[f'{prefix}_calls_{dr[0]}_{dr[1]}_cnt_{day[0]}'] = len([x for x in calling if x in called])
    print('duration day feature count:', len(result))
    return result


# 通话时段 + 时间轴进行衍生
def time_interval_day(dataObj):
    prefix = 'yysCall'
    result = dict()
    time_interval_list = [
        ('early_morning', 5, 30, 9, 0),
        ('morning', 9, 0, 11, 30),
        ('nooning', 11, 30, 13, 30),
        ('afternoon', 13, 30, 17, 30),
        ('toward_evening', 17, 30, 19, 30),
        ('evening', 19, 30, 23, 30),
        ('small_hour', 23, 30, 1, 30),
        ('midnight', 1, 30, 5, 30)
    ]
    last_modify_time = dataObj.last_modify_time
    df_callRecord_3day = dataObj.df_callRecord[(last_modify_time - dataObj.df_callRecord['time']).dt.days <= 3]
    df_callRecord_15day = dataObj.df_callRecord[(last_modify_time - dataObj.df_callRecord['time']).dt.days <= 15]
    day_list = [
        ('3d', df_callRecord_3day),
        ('7d', dataObj.df_callRecord_7day),
        ('15d', df_callRecord_15day),
        ('30d', dataObj.df_callRecord_1m),
        ('90d', dataObj.df_callRecord_3m),
        ('180d', dataObj.df_callRecord)
    ]
    for day in day_list:
        # temp是近x天的通话
        data = day[1][['time', 'peer_number', 'duration', 'dial_type']]
        temp = data.copy()
        temp['hour'] = data['time'].dt.hour
        temp['minute'] =  data['time'].dt.minute
        for ti in time_interval_list:
            if ti[0] == 'small_hour':
                # 从23:30 到 23:59
                time_range1 = temp[(temp.hour>=ti[1]) & (temp.minute>=ti[2]) & (temp.minute<=59)]
                # 从00:00 到 1:30
                time_range2 = temp[(temp.hour>=0) & (temp.minute>0) & (temp.hour<=ti[3]) & (temp.minute<ti[4])]
                match_df = pd.concat([time_range1, time_range2], axis=0)
            else:
                match_df = temp[(temp.hour>=ti[1]) & (temp.minute>=ti[2]) & (temp.hour<=ti[3]) & (temp.minute<ti[4])]
            # 近x天通话时段在(y_hour: y_minute)-(z_hour: z_minute)的通话次数
            result[f'{prefix}_call_{ti[0]}_cnt_{day[0]}'] = match_df.shape[0]
            # 近x天通话时段在(y_hour: y_minute)-(z_hour: z_minute)的通话次数比例
            result[f'{prefix}_call_{ti[0]}_rate_{day[0]}'] = division(match_df.shape[0], temp.shape[0])
            # 近x天通话时段在(y_hour: y_minute)-(z_hour: z_minute)的通话时长
            result[f'{prefix}_call_{ti[0]}_time_{day[0]}'] = sum(match_df['duration'].values.tolist())
            # 近x天通话时段在(y_hour: y_minute)-(z_hour: z_minute)的联系人个数
            result[f'{prefix}_contacter_{ti[0]}_cnt_{day[0]}'] = len(set(match_df['peer_number'].values))
    print('time interval day feature count:', len(result))
    return result


# 联系人标签 + 时间轴衍生
def contact_tag(dataObj):
    prefix = 'yysCall'
    result = dict()
    last_modify_time = dataObj.last_modify_time
    df_callRecord_3day = dataObj.df_callRecord[(last_modify_time - dataObj.df_callRecord['time']).dt.days <= 3]
    df_callRecord_15day = dataObj.df_callRecord[(last_modify_time - dataObj.df_callRecord['time']).dt.days <= 15]
    day_list = [
        ('3d', df_callRecord_3day),
        ('7d', dataObj.df_callRecord_7day),
        ('15d', df_callRecord_15day),
        ('30d', dataObj.df_callRecord_1m),
        ('90d', dataObj.df_callRecord_3m),
        ('180d', dataObj.df_callRecord)
    ]
    phones = ['110', '120', '119']
    for day in day_list:
        temp = day[1][['peer_number', 'duration', 'dial_type']]
        for phone in phones:
            # match_df 是近x天与phone的通话记录，phone属于110，120，199
            match_df = temp[temp.peer_number==phone]
            # 近x天与110,120,119通话次数
            result[f'{prefix}_call_{phone}_cnt_{day[0]}'] = match_df.shape[0]
            # 近x天与110,120,119主叫次数
            result[f'{prefix}_call_dial_{phone}_cnt_{day[0]}'] = match_df[match_df.dial_type == 'DIAL'].shape[0]
            # 近x天与110,120,119被叫次数
            result[f'{prefix}_call_dialed_{phone}_cnt_{day[0]}'] = match_df[match_df.dial_type == 'DIALED'].shape[0]
            # 近x天与110,120,119通话次数占比
            result[f'{prefix}_call_{phone}_rate_{day[0]}'] = division(match_df.shape[0], temp.shape[0])
            # 近x天与110,120,119主叫时长
            result[f'{prefix}_call_dial_{phone}_time_{day[0]}'] = sum(match_df['duration'][match_df.dial_type == 'DIAL'].values)
            # 近x天与110,120,119被叫时长
            result[f'{prefix}_call_dialed_{phone}_time_{day[0]}'] = sum(match_df['duration'][match_df.dial_type == 'DIALED'].values)
            call_duration = sum(match_df['duration'].values.tolist())
            # 近x天与110,120,119的通话时长
            result[f'{prefix}_call_{phone}_time_{day[0]}'] = call_duration
            # 近x天与110,120,119的通话时长占比
            result[f'{prefix}_call_{phone}_time_rate_{day[0]}'] = division(call_duration, sum(temp['duration'].values.tolist()))
    print('contact tag feature count:', len(result))
    return result


# 通话费用 + 时间轴衍生
def fee_day(dataObj):
    prefix = 'yysCall'
    result = dict()
    last_modify_time = dataObj.last_modify_time
    df_callRecord_3day = dataObj.df_callRecord[(last_modify_time - dataObj.df_callRecord['time']).dt.days <= 3]
    df_callRecord_15day = dataObj.df_callRecord[(last_modify_time - dataObj.df_callRecord['time']).dt.days <= 15]
    day_list = [
        #('3d', df_callRecord_3day),
        #('7d', dataObj.df_callRecord_7day),
        #('15d', df_callRecord_15day),
        ('30d', dataObj.df_callRecord_1m),
        ('90d', dataObj.df_callRecord_3m),
        ('180d', dataObj.df_callRecord)
    ]
    # 费用区间，单位是分
    fee_range = [(0, 20),(20, 50),(50, 100),(100, 500),(500, 'up')]
    for day in day_list:
        temp = day[1][['peer_number', 'fee']]
        for fr in fee_range:
            if fr[1] == 'up':
                match_df = temp[temp.fee > fr[0]]
            else:
                match_df = temp[(temp.fee > fr[0]) & (temp.fee <= fr[1])]
            # 近x天通话费用在(y,z]的通话次数
            result[f'{prefix}_call_fee_{fr[0]}_{fr[1]}_cnt_{day[0]}'] = match_df.shape[0]
            # 近x天通话费用在(y,z]的通话次数占比
            result[f'{prefix}_call_fee_{fr[0]}_{fr[1]}_rate_{day[0]}'] = division(match_df.shape[0], temp.shape[0])
            # 近x天通话费用在(y,z]的联系人个数
            result[f'{prefix}_contacter_call_fee_{fr[0]}_{fr[1]}_cnt_{day[0]}'] = len(set(match_df['peer_number'].values))
    print('fee day feature count:', len(result))
    return result


# 被叫，主叫次数中位数
def median_time(dataObj):
    prefix = 'yysCall'
    result = dict()
    last_modify_time = dataObj.last_modify_time
    df_call = dataObj.df_callRecord
    df_callRecord_3day = df_call[(last_modify_time - df_call['time']).dt.days <= 3]
    df_callRecord_15day = df_call[(last_modify_time - df_call['time']).dt.days <= 15]
    day_list = [
        ('3d', df_callRecord_3day),
        ('7d', dataObj.df_callRecord_7day),
        ('15d', df_callRecord_15day),
        ('30d', dataObj.df_callRecord_1m),
        ('90d', dataObj.df_callRecord_3m),
        ('180d', dataObj.df_callRecord)
    ]
    # 每天被叫、主叫次数中位数
    temp = df_call.copy()
    temp['year'] = df_call['time'].dt.year
    temp['month'] = df_call['time'].dt.month
    temp['day'] = df_call['time'].dt.day
    for day in day_list:
        temp_df = day[1][['time', 'dial_type']]
        temp = temp_df.copy()
        temp['year'] = temp_df['time'].dt.year
        temp['month'] = temp_df['time'].dt.month
        temp['day'] = temp_df['time'].dt.day
        temp = temp.groupby(['year', 'month', 'day'])
        dial_cnt_array = []
        dialed_cnt_array = []
        # data是近x天某天的通话记录
        for index, data in temp:
            dial_cnt_array.append(data[data.dial_type=='DIAL'].shape[0])
            dialed_cnt_array.append(data[data.dial_type=='DIALED'].shape[0])
        # 近x天每天主叫次数中位数
        result[f'{prefix}_dial_cnt_median_{day[0]}'] = cal_median(dial_cnt_array)
        # 近x天每天被叫次数中位数
        result[f'{prefix}_dialed_cnt_median_{day[0]}'] = cal_median(dialed_cnt_array)

    time_limit_list = []
    time_limit_list.append(last_modify_time)
    for i in (1,2,3,4,5,6):
       time_limit_list.append(last_modify_time - datetime.timedelta(days = 30*i))
    dial_cnt_every_month = []
    dialed_cnt_every_month = []
    for i in range(len(time_limit_list)):
        if (i+1) < len(time_limit_list):
            temp = df_call[(df_call.time>time_limit_list[i+1]) & (df_call.time<=time_limit_list[i])]
            dial_cnt_every_month.append(temp[temp.dial_type=='DIAL'].shape[0])
            dialed_cnt_every_month.append(temp[temp.dial_type=='DIALED'].shape[0])
    # 近3个月，6个月每月被叫次数中位数
    result[f'{prefix}_dialed_cnt_median_3m'] = cal_median(dialed_cnt_every_month[0:3])
    result[f'{prefix}_dialed_cnt_median_6m'] = cal_median(dialed_cnt_every_month)
    # 近3个月，6个月每月主叫次数中国年位数
    result[f'{prefix}_dial_cnt_median_3m'] = cal_median(dial_cnt_every_month[0:3])
    result[f'{prefix}_dial_cnt_median_6m'] = cal_median(dial_cnt_every_month)
    print('yysCall median time count:', len(result))
    return result

# 通话汇总
def call_summary(dataObj):
    prefix = 'yysCall'





# 通话记录特征汇总
def yysCall(dataObj):
    head = 'yysCall'
    result = dict()
    # 通话时长 + 时间轴衍生
    dd = duration_day(dataObj)
    # 通话时段 + 时间轴衍生
    tid = time_interval_day(dataObj)
    # 号码标签 + 时间轴衍生
    ct = contact_tag(dataObj)
    # 费用区间 + 时间轴衍生
    fd = fee_day(dataObj)
    mt = median_time(dataObj)
    #result.update(dd)
    #result.update(tid)
    # result.update(ct)
    #result.update(fd)
    result.update(mt)
    return result

