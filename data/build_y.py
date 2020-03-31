from data.y_annual import build_compa
from data.y_quarter import build_compq
import pandas as pd
import os
from global_settings import DATA_FOLDER, ccm, groups
import pickle
from tools.utils import y_filter
from datetime import datetime


def run_build_annual_y(permnos, group):
    compa = build_compa(permnos)
    permnos = set(compa['permno'].tolist())
    compa_a = compa.set_index(['permno', 'fyear', 'fqtr'], inplace=False)
    compa_a = compa_a.sort_index(inplace=False)
    compa_id = compa_a.iloc[:, :5]
    compa_a = compa_a.iloc[:, 5:]
    compa_a = y_filter(compa_a, 'annual')

    compa_aoa = pd.DataFrame()
    compa_5o5 = pd.DataFrame()
    for permno in permnos:
        compa_a_ = compa_a.loc[[permno], :]
        compa_a_s1_ = compa_a_.shift(1)
        compa_a_s5_ = compa_a_.shift(5)
        compa_aoa_ = (compa_a_ / compa_a_s1_) - 1
        compa_5o5_ = (compa_a_ / compa_a_s5_).pow(1/5) - 1
        compa_aoa = pd.concat([compa_aoa, compa_aoa_], axis=0)
        compa_5o5 = pd.concat([compa_5o5, compa_5o5_], axis=0)
    compa_aoa.columns = [col_names + '_aoa' for col_names in compa_a.columns]
    compa_5o5.columns = [col_names + '_5o5' for col_names in compa_a.columns]

    y_a = pd.concat([compa_id, compa_a, compa_aoa, compa_5o5], axis=1)

    with open(os.path.join(DATA_FOLDER, 'annual_y', '_'.join(['y', group]) + '.pkl'), 'wb') as handle:
        pickle.dump(y_a, handle)


def run_build_quarter_y(permnos, group):
    compq = build_compq(permnos)
    permnos = set(compq['permno'].tolist())
    compq_q = compq.set_index(['permno', 'fyearq', 'fqtr'], inplace=False)
    compq_q = compq_q.sort_index(inplace=False)
    compq_id = compq_q.iloc[:, :5]
    compq_q = compq_q.iloc[:, 5:]
    compq_q = y_filter(compq_q, 'quarter')

    compq_qoq = pd.DataFrame()
    for permno in permnos:
        compq_q_ = compq_q.loc[[permno], :]
        compq_q_s1_ = compq_q_.shift(1)
        compq_qoq_ = (compq_q_ - compq_q_s1_) / compq_q_s1_
        compq_qoq = pd.concat([compq_qoq, compq_qoq_], axis=0)

    compq_aoa = pd.DataFrame()
    compq_5o5 = pd.DataFrame()
    for quarter in [1, 2, 3, 4]:
        compq_a = compq[compq['fqtr'] == quarter]
        compq_a = compq_a.set_index(['permno', 'fyearq', 'fqtr'], inplace=False)
        compq_a = compq_a.sort_index(inplace=False)
        compq_a = compq_a.iloc[:, 5:]
        compq_a = y_filter(compq_a, 'quarter')
        for permno in permnos:
            try:
                compq_a_ = compq_a.loc[[permno], :]
                compq_a_s1_ = compq_a_.shift(1)
                compq_a_s5_ = compq_a_.shift(5)
                compq_aoa_ = (compq_a_ / compq_a_s1_) - 1
                compq_5o5_ = (compq_a_ / compq_a_s5_).pow(1/5) - 1
                compq_aoa = pd.concat([compq_aoa, compq_aoa_], axis=0)
                compq_5o5 = pd.concat([compq_5o5, compq_5o5_], axis=0)
            except KeyError:
                pass

    compq_qoq.columns = [col_names + '_qoq' for col_names in compq_q.columns]
    compq_aoa.columns = [col_names + '_aoa' for col_names in compq_a.columns]
    compq_5o5.columns = [col_names + '_5o5' for col_names in compq_a.columns]
    compq_a5oa5 = pd.concat([compq_aoa, compq_5o5], axis=1)
    y_q = pd.concat([compq_id, compq_q], axis=1)
    y_q = pd.merge(y_q, compq_qoq, left_index=True, right_index=True)
    y_q = pd.merge(y_q, compq_a5oa5, left_index=True, right_index=True)

    with open(os.path.join(DATA_FOLDER, 'quarter_y', '_'.join(['y', group]) + '.pkl'), 'wb') as handle:
        pickle.dump(y_q, handle)


def run_build_y(group):
    permnos = tuple([_ for _ in ccm['permno'] if str(_)[:2] == group])
    run_build_annual_y(permnos, group)
    run_build_quarter_y(permnos, group)


if __name__ == '__main__':
    for group in groups:
        print(f'{datetime.now()} Working on group with permno starting with ' + group)
        run_build_y(group)
    # pool = Pool(14)
    # pool.map(run_build_xy, years)
