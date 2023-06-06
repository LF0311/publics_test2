import streamlit as st
import time
import numpy as np
import random
import datetime
import pandas as pd
import struct
import requests


def read_files_split(df):
    # 重命名列名
    time_list = []
    n_list = []
    e_list = []

    for tme in range(len(df[0])):
        time_list.append(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        n_list.append(31.976 + 0.01 * df[11][tme])
        e_list.append(118.846 + 0.01 * df[11][tme])

    df['T'] = time_list
    df['N'] = n_list
    df['E'] = e_list

    df.columns = ['Frame', 'X_Accel', 'Y_Accel', 'Z_Accel', 'X_Gyro', 'Y_Gyro', 'Z_Gyro', 'X_Mag', 'Y_Mag', 'Z_Mag',
                  'Audio', 'Id', 'Audio_VAD', 'Not_use', 'Location', 'T', 'N', 'E']
    # 删除Location列
    df['Audio'] = df['Audio'].apply(lambda x: x / 100)
    # df['N'] = df['N'].apply(lambda x: float(x) / 100)
    # df['E'] = df['E'].apply(lambda x: float(x) / 100)
    df1 = df.drop(['Location', 'Not_use'], axis=1)
    return df1



def process_udp(obj_txt, data):
    k = 0
    while True:
        if data[0 + k * 74:k * 74 + 1] == b'':
            # obj.close()
            break
        if data[0 + k * 74:k * 74 + 1] == b'\xbb' and data[k * 74 + 1:k * 74 + 2] == b'\xbb':
            data_sensor = data[k * 74 + 4:k * 74 + 30]  # fp.read(24)
            count = len(data_sensor) / 2
            var = struct.unpack('h' * int(count), data_sensor)
            print(k, var)
            data_sensor_first = data[k * 74 + 28:k * 74 + 30]  # fp.read(2)

            # var0 = data_sensor_first.decode('utf-8')
            data_sensor_next = data[k * 74 + 30:k * 74 + 64]  # fp.read(34)
            if b'\x54\x3a' in data_sensor_first:
                var0 = data_sensor_first.decode()
                if b'\x00\x00\x00\x00' in data_sensor_next:
                    var_list = []
                    var_list.append(k)
                    for v in var:
                        var_list.append(v)
                    # var_list.append((var0 + var1))
                    obj_txt.write(str(var_list).strip('[]') + '\n')
                    # k += 1
                else:
                    var1 = data_sensor_next.decode('utf-8')
                    data_sensor_final = data[k * 74 + 64:k * 74 + 74]  # fp.read(10)
                    print(var, var0 + var1)
                    var_list = []
                    var_list.append(k)
                    for v in var:
                        var_list.append(v)
                    # var_list.append((var0 + var1))
                    obj_txt.write(str(var_list).strip('[]') + ', ' + var0 + var1 + '\n')
            else:
                var0 = str(data_sensor_first)
                if b'\x00\x00\x00\x00' in data_sensor_next:
                    var_list = []
                    var_list.append(k)
                    for v in var:
                        var_list.append(v)
                    # var_list.append((var0 + var1))
                    obj_txt.write(str(var_list).strip('[]') + '\n')
                    # k += 1
                else:
                    var1 = data_sensor_next.decode('utf-8')
                    data_sensor_final = data[k * 74 + 64:k * 74 + 74]  # fp.read(10)
                    print(var, var0 + var1)
                    var_list = []
                    var_list.append(k)
                    for v in var:
                        var_list.append(v)
                    # var_list.append((var0 + var1))
                    obj_txt.write(str(var_list).strip('[]') + ', ' + var0 + var1 + '\n')
        k += 1
    print("已生成txt数据文件！")






st.markdown(
    f'''
        <style>
            .reportview-container .sidebar-content {{
                padding-top: {0}rem;
            }}
            .appview-container .main .block-container {{
                {f'max-width: 100%;'}
                padding-top: {0}rem;
                padding-right: {1}rem;
                padding-left: {1}rem;
                padding-bottom: {0}rem;
                overflow: auto;
            }}
        </style>
        ''',
    unsafe_allow_html=True,
)

st.subheader("  ")

colmns0 = st.columns([1,8,1], gap="medium")

with colmns0[1]:
    st.markdown(
        '<nobr><p style="text-align: center;font-family:sans serif; color:Black; font-size: 32px; font-weight: bold">环境传感器目标识别平台</p></nobr>',
        unsafe_allow_html=True)

with colmns0[1]:
    # st.markdown('###')

    timestr = time.strftime('%Y-%m-%d %H:%M:%S')
    st.markdown(
        '<nobr><p style="text-align: center;font-family:sans serif; color:Black; font-size: 20px;">{}</p></nobr>'.format(timestr),
        unsafe_allow_html=True)


colmns = colmns0[1].columns([1,1,1,1], gap="small")
button1 = colmns[0].button(' 开始执行 ')
button2 = colmns[1].button(' 结束指令 ')
button3 = colmns[2].button(' 刷新页面 ')
button4 = colmns[3].button(' 重置页面 ')

# 本地IP地址和端口号
LOCAL_IP = "192.168.2.10"
# LOCAL_PORT = 0  # 选择一个空闲端口，系统会自动分配

# 服务器IP地址和端口号
UDP_IP = "192.168.2.50"
UDP_PORT = 1438

# 指令数据
command_real_time = bytearray([0x55, 0xAA, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA, 0x55])
command_history = bytearray([0x55, 0xAA, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xAA, 0x55])
sj_mode_control = bytearray([0x55, 0xAA, 0x10, 0x02, 0x01, 0x01, 0x00])
zz_mode_control = bytearray([0x55, 0xAA, 0x20, 0x02, 0x02, 0x02, 0x00])


if button1:
    start_time = time.time()
    while True:
        st.markdown(button2)
        if button2 or button3 or button4:
            # st.markdown('终止发送')
            print('终止发送')
            break
        else:
            first_elapsed_time = time.time() - start_time
            # print(elapsed_time)

            if first_elapsed_time >= 30:
                print("已等待30秒，重新接收数据")
                start_time = time.time()
                continue
            else:
                # 读取文件，解析数据
                read_file_df = pd.read_csv('./sensors_data.txt', sep=',', header=None)
                final_read_file_df = read_files_split(read_file_df)

                sensor_dfs = {}

                # 获取id列中的唯一值
                unique_ids = final_read_file_df['Id'].unique()
                unique_ids = sorted(unique_ids)
                for id_value in unique_ids:
                    # 根据id值筛选数据
                    subset = final_read_file_df[final_read_file_df['Id'] == id_value]
                    subset.reset_index(drop=False, inplace=True)
                    # 将分割后的数据框存储到字典中
                    sensor_dfs[id_value] = subset

                for sensID in unique_ids:
                    trans_data_tmp = {}
                    trans_data_tmp.update(
                        {
                            'CGQID': str(sensID),
                            'JD': str(sensor_dfs[sensID]['N'].iloc[0]),
                            'WD': str(sensor_dfs[sensID]['E'].iloc[0]),
                            'SBSJ': str(sensor_dfs[sensID]['T'].iloc[0]),
                            'SZJSD': list(np.array(list(abs(sensor_dfs[sensID]['X_Accel']))) + 500*random.random()),
                            'CTL': list(np.array(list(abs(sensor_dfs[sensID]['X_Mag']))) + 500*random.random()),
                            'ZS': list(np.array(list(abs(sensor_dfs[sensID]['Audio']))) + 500*random.random()),
                        }
                    )
                    url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendSensorInfo'
                    print(trans_data_tmp)
                    response_tmp = requests.post(url, json=trans_data_tmp)
                    # print(trans_data_tmp)
                time.sleep(5)
                print('休眠5s，重新发送Button1')


if button3:
    start_time = time.time()
    while True:
        st.markdown(button2)
        if button1 or button2 or button4:
            st.markdown('终止发送')
            print('终止发送Button3')
            break
        else:
            first_elapsed_time = time.time() - start_time
            # print(elapsed_time)
            if first_elapsed_time >= 30:
                print("已等待30秒，重新接收数据")
                start_time1 = time.time()
                continue
            else:
                # 读取文件，解析数据
                read_file_df = pd.read_csv('./sensors_data.txt', sep=',', header=None)
                final_read_file_df = read_files_split(read_file_df)

                sensor_dfs = {}

                # 获取id列中的唯一值
                unique_ids = final_read_file_df['Id'].unique()
                unique_ids = sorted(unique_ids)
                for id_value in unique_ids:
                    # 根据id值筛选数据
                    subset = final_read_file_df[final_read_file_df['Id'] == id_value]
                    subset.reset_index(drop=False, inplace=True)
                    # 将分割后的数据框存储到字典中
                    sensor_dfs[id_value] = subset

                trans_data_1 = {}
                trans_data_1.update(
                    {
                        'JDMIN': final_read_file_df['N'].min(),
                        'JDMAX': final_read_file_df['N'].max(),
                        'WDMIN': final_read_file_df['E'].min(),
                        'WDMAX': final_read_file_df['E'].max(),
                        'MBLB': '人员',
                        'MBGS': '1',
                        'SBXH': '振动',
                        'FXSJ': final_read_file_df['T'][0],
                        'IDLIST': [1]
                    }
                )
                url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendTargetInfo'
                print(trans_data_1)
                response = requests.post(url, json=trans_data_1)


                for sensID in unique_ids:
                    trans_data_tmp = {}
                    trans_data_tmp.update(
                        {
                            'CGQID': str(sensID),
                            'JD': str(sensor_dfs[sensID]['N'].iloc[0]),
                            'WD': str(sensor_dfs[sensID]['E'].iloc[0]),
                            'SBSJ': str(sensor_dfs[sensID]['T'].iloc[0]),
                            'SZJSD': list(np.array(list(abs(sensor_dfs[sensID]['X_Accel']))) + 500*random.random()),
                            'CTL': list(np.array(list(abs(sensor_dfs[sensID]['X_Mag']))) + 500*random.random()),
                            'ZS': list(np.array(list(abs(sensor_dfs[sensID]['Audio']))) + 500*random.random()),
                        }
                    )
                    url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendSensorInfo'
                    print(trans_data_tmp)
                    response_tmp = requests.post(url, json=trans_data_tmp)


                time.sleep(5)
                print('休眠5s，重新发送Button3')


if button4:
    start_time = time.time()
    while True:
        st.markdown(button2)
        if button1 or button2 or button3:
            # st.markdown('终止发送')
            print('终止发送Button4')
            break
        else:
            first_elapsed_time = time.time() - start_time
            # print(elapsed_time)
            if first_elapsed_time >= 30:
                print("已等待30秒，重新接收数据")
                start_time1 = time.time()
                continue
            else:
                # 读取文件，解析数据
                read_file_df = pd.read_csv('./sensors_data.txt', sep=',', header=None)
                final_read_file_df = read_files_split(read_file_df)

                sensor_dfs = {}

                # 获取id列中的唯一值
                unique_ids = final_read_file_df['Id'].unique()
                unique_ids = sorted(unique_ids)
                for id_value in unique_ids:
                    # 根据id值筛选数据
                    subset = final_read_file_df[final_read_file_df['Id'] == id_value]
                    subset.reset_index(drop=False, inplace=True)
                    # 将分割后的数据框存储到字典中
                    sensor_dfs[id_value] = subset

                trans_data_1 = {}
                trans_data_1.update(
                    {
                        'JDMIN': final_read_file_df['N'].min(),
                        'JDMAX': final_read_file_df['N'].max(),
                        'WDMIN': final_read_file_df['E'].min(),
                        'WDMAX': final_read_file_df['E'].max(),
                        'MBLB': '人员',
                        'MBGS': '1',
                        'SBXH': '振动',
                        'FXSJ': final_read_file_df['T'][0],
                        'IDLIST': [2]
                    }
                )
                url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendTargetInfo'
                print(trans_data_1)
                response = requests.post(url, json=trans_data_1)


                for sensID in unique_ids:
                    trans_data_tmp = {}
                    trans_data_tmp.update(
                        {
                            'CGQID': str(sensID),
                            'JD': str(sensor_dfs[sensID]['N'].iloc[0]),
                            'WD': str(sensor_dfs[sensID]['E'].iloc[0]),
                            'SBSJ': str(sensor_dfs[sensID]['T'].iloc[0]),
                            'SZJSD': list(np.array(list(abs(sensor_dfs[sensID]['X_Accel']))) + 500*random.random()),
                            'CTL': list(np.array(list(abs(sensor_dfs[sensID]['X_Mag']))) + 500*random.random()),
                            'ZS': list(np.array(list(abs(sensor_dfs[sensID]['Audio']))) + 500*random.random()),
                        }
                    )
                    url = 'http://51.51.51.15:9011/api/WLW_MLFW/sendSensorInfo'
                    print(trans_data_tmp)
                    response_tmp = requests.post(url, json=trans_data_tmp)


                time.sleep(5)
                print('休眠5s，重新发送Button4')

# 按钮字体
st.markdown("""<style>p, ol, ul, dl
{
margin: 0px 0px 1rem;
padding: 0px;
font-size: 1.0rem;
font-weight: 1000;
}
</style>""", unsafe_allow_html=True)

st.markdown("""<style> div.stButton > button:first-child {
background-color: white;
color: black;
height:3em; 
width:8em; 
border-radius:10px 10px 10px 10px;
border: 3px solid #008CBA;
}
</style>""", unsafe_allow_html=True)

st.markdown("""<style> 
#root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.css-uf99v8.egzxvld5 > div.block-container.css-z5fcl4.egzxvld4 > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(1) > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(5) > div > div.css-c6gdys.edb2rvg0 > div > p {
font-size: 4px;
}
</style>""", unsafe_allow_html=True)
st.markdown("""<style> 
#root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.css-uf99v8.egzxvld5 > div.block-container.css-z5fcl4.egzxvld4 > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(1) > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(4) > div > div.css-c6gdys.edb2rvg0 > div > p {
font-size: 4px;
}
</style>""", unsafe_allow_html=True)

st.markdown("""<style> 
#root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.css-uf99v8.egzxvld5 > div.block-container.css-z5fcl4.egzxvld4 > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(1) > div:nth-child(1) > div > div.css-ocqkz7.e1tzin5v3 > div:nth-child(2) > div:nth-child(1) > div > div:nth-child(6) > div > div > div > div > div > div > p {
font-size: 4px;
}
</style>""", unsafe_allow_html=True)
st.markdown("""<style> div.stButton > button:first-child {
background-color: white;
color: black;
height:3em; 
width:8em; 
border-radius:10px 10px 10px 10px;
border: 3px solid #008CBA;
}
</style>""", unsafe_allow_html=True)

st.markdown("""<style> div.stButton > button:hover {
background-color: #008CBA;
color: white;
}
</style>""", unsafe_allow_html=True)
