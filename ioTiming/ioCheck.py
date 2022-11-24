from __future__ import annotations
from typing import AnyStr, List, Tuple, Dict, Union, Set, Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from dataBase import DbDataBase
    from dataBase.dbHNet import DbHNet
    from dataBase.dbHInstTerm import DbHInstTerm

import pandas as pd
import os
from collections import Counter
import matplotlib.pyplot as plt
from utils import CoordinateProcess, Print


class IOChecker:
    __DF_COLS = ['direction', 'port_x', 'port_y', 'reg_x', 'reg_y', 'path_delay', 'clock_latency', 'manhattan_distance', 'clk_name', 'clk_period', 'reg_name']
    __IDEAL_CLOCK__ = True
    __LIB_SETUP__ = 0.020
    __UNCERTAINTY__ = 0.040

    def __init__(self, db: DbDataBase, block_io_csv_dict: Dict[str, str]):
        Print(f'IO Checker start')
        self.db = db
        self.block_io_info_map: Dict[str, pd.DataFrame] = {}
        for block_name, csv_file in block_io_csv_dict.items():
            Print(f'Loading {block_name} interface information file')
            self.block_io_info_map[block_name] = pd.read_csv(csv_file, index_col=0).round(5)
        self.net_ends: List[List[DbHInstTerm]] = []

        self.total_raw_df = pd.DataFrame()
        self.total_io_info_df = pd.DataFrame()

        self.regular_io_info_df = pd.DataFrame()
        self.ft_raw_io_info_df = pd.DataFrame()
        self.regular_io_info_dict = {}

        self.ft_io_info_df = pd.DataFrame()
        self.ft_io_info_dict = {}

        self.__preprocessIoInfo()
        self.__deriveConnectivity()
        self.__composeIoInfo()

        self.__classifyRegularIoInfo()
        self.__classifyFtIoInfo()

    def __preprocessIoInfo(self):
        Print(f'Preprocessing block one-side interface info dataframe and constructing total dataframe')
        dfs = []
        for block_name, df in self.block_io_info_map.items():
            for hInst in [ii for ii in self.db.chip.hInst.treeHInsts.values() if ii.cell == block_name]:
                new_def = df.copy(deep=True)
                new_def.index = hInst.name + '/' + df.index
                new_def['module'] = hInst.cell
                new_def['port_name'] = df.index
                new_def['instterm_name'] = new_def.index
                dfs.append(new_def[['instterm_name', 'port_name', 'module'] + self.__DF_COLS])
        self.total_raw_df = pd.concat(dfs)

    def __deriveConnectivity(self):
        hNet_list = []
        for hInst in [self.db.chip.hInst] + [hInst for hInst in self.db.chip.hInst.treeHInsts.values() if hInst.cell not in self.block_io_info_map]:
            hNet_list += list([hNet for hNet in hInst.hNets.values() if hNet.hTerms == {}])
        hNets_cnt = len(hNet_list)
        step = int(hNets_cnt / 10)
        self.net_ends = [[] for _ in range(0, hNets_cnt)]
        Print(f'Deriving IO mapping, total {hNets_cnt} hNets to be iterated.')

        for idx, hNet in enumerate(hNet_list):
            if (idx + 1) % step == 0:
                Print(f'  {(idx+1) // step}0% is done.')
            self.__iterateEndOfEnd(hNet, idx)
            self.net_ends[idx].sort(key=lambda hInstTerm:hInstTerm.hTerm.direction, reverse=True)

    def __iterateEndOfEnd(self, hNet: DbHNet, idx: int):
        for hInstTerm in hNet.hInstTerms.values():
            if hInstTerm.hInst.cell in self.block_io_info_map:
                self.net_ends[idx].append(hInstTerm)
            else:
                self.__iterateEndOfEnd(hInstTerm.downHNet, idx)

    def __composeIoInfo(self):
        Print(f'Composing interface information dataframe')
        Print(f'  Choose nets with 2 connections')
        valid_net_ends = [ii for ii in self.net_ends if len(ii) == 2]
        Print(f'  Filter io pairs based on total dataframe')
        io_pairs = [ii for ii in valid_net_ends if ii[0].name in self.total_raw_df.index and ii[1].name in self.total_raw_df.index]
        s = [ii[0].name for ii in io_pairs]
        e = [ii[1].name for ii in io_pairs]
        Print(f'  Build start-dataframe and end-dataframe pair')
        s_df = self.total_raw_df.loc[s]
        e_df = self.total_raw_df.loc[e]
        Print(f'  Merge start-end dataframe')
        for data_type in s_df.columns:
            self.total_io_info_df['ref' + data_type] = s_df[data_type].values
            self.total_io_info_df['tar' + data_type] = e_df[data_type].values
        self.total_io_info_df.index = s_df.index
        Print(f'  Split total io info dataframe to regular  type and feedthrough type')
        self.regular_io_info_df = self.total_io_info_df[~self.total_io_info_df['ref_reg_name'].str.contains('port-') & ~self.total_io_info_df['tar_reg_name'].str.contains('port-')]
        self.ft_raw_io_info_df = self.total_io_info_df[self.total_io_info_df['ref_reg_name'].str.contains('port-') | self.total_io_info_df['tar_reg_name'].str.contains('port-')]
        Print(f'  Remove regular io info CDC path')
        self.regular_io_info_df = self.regular_io_info_df[self.regular_io_info_dict['ref_clk_period'] == self.regular_io_info_df['tar_clk_period']]
        Print(f'  Calculate regular io info')
        self.regular_io_info_df['total_manhattan_distance'] = self.regular_io_info_df['ref_manhattan_distance'] + self.regular_io_info_df['tar_manhattan_distance']
        self.regular_io_info_df['total_path_delay'] = self.regular_io_info_df['ref_path_delay'] + self.regular_io_info_df['tar_path_delay']
        self.regular_io_info_df['skew'] = self.regular_io_info_df['tar_clock_latency'] - self.regular_io_info_df['ref_clock_latency']
        T = self.regular_io_info_df['ref_clk_period']
        skew = self.regular_io_info_df['skew']
        delay = self.regular_io_info_df['total_path_delay']
        if self.__IDEAL_CLOCK__:
            self.regular_io_info_df['setup_slack'] = T - delay - self.__LIB_SETUP__ - self.__UNCERTAINTY__
        else:
            self.regular_io_info_df['setup_slack'] = T + skew - delay - self.__LIB_SETUP__ - self.__UNCERTAINTY__

        Print(f'  Calculate feedthrough io info')
        ref_cols = [ii for ii in self.ft_raw_io_info_df.columns if 'ref_' in ii]
        tar_cols = [ii for ii in self.ft_raw_io_info_df.columns if 'tar_' in ii]
        ft_cols = list(self.ft_raw_io_info_df.columns) + ['total_manhattan_distance', 'total_path_delay', 'skew', 'setup_slack', 'ft_path']
        ft_data = []
        ft_index = []
        ft_start_pts = self.ft_raw_io_info_df[~self.ft_raw_io_info_df['ref_reg_name'].str.contains('port-')]['ref_instterm_name']
        ft_start_pts_len = len(ft_start_pts)
        idx = 0
        step = int(ft_start_pts_len / 10)
        Print(f'    {ft_start_pts_len} ft paths to be iterated')
        for instterm in ft_start_pts:
            idx += 1
            if idx % step == 0:
                Print(f'    {idx // step}0% is done')
            series = self.iterateFtPath(instterm)
            if series:
                _row = []
                for ref, tar in zip(series[0][ref_cols], series[-1][tar_cols]):
                    _row += [ref, tar]
                ft_path = []
                for ss in series[: -1]:
                    ft_in_instterm = ss['tar_instterm_name']
                    ft_in_instterm_loc = (ss['tar_port_x'], ss['tar_port_y'])
                    ft_out_instterm = os.path.dirname(ft_in_instterm) + '/' + ss['tar_reg_name'].replace('port-', '')
                    ft_out_instterm_loc = (ss['tar_reg_x'], ss['tar_reg_y'])
                    ft_dist = ss['tar_manhattan_distance']
                    ft_delay = ss['tar_path_delay']
                    ft_path.append([ft_in_instterm, ft_out_instterm, ft_dist, ft_delay, ft_in_instterm_loc, ft_out_instterm_loc])
                total_dist = series[0]['ref_manhattan_distance'] + series[-1]['tar_manhattan_distance'] + sum([ii[2] for ii in ft_path])
                total_delay = series[0]['ref_path_delay'] + series[-1]['tar_path_delay'] + sum([ii[3] for ii in ft_path])
                skew = series[-1]['tar_clock_latency'] - series[0]['ref_clock_latency']
                if self.__IDEAL_CLOCK__:
                    setup_slack = series[0]['ref_clk_period'] - total_delay - self.__LIB_SETUP__ - self.__UNCERTAINTY__
                else:
                    setup_slack = series[0]['ref_clk_period'] - total_delay - self.__LIB_SETUP__ - self.__UNCERTAINTY__ + skew
                _row += [total_dist, total_delay, skew, setup_slack, ft_path]
                ft_data.append(_row)
                ft_index.append(series[0].name)
        self.ft_io_info_df = pd.DataFrame(data=ft_data, index=ft_index, columns=ft_cols)
        Print(f'  Remove feedthrough io info CDC path')
        self.ft_io_info_df = self.ft_io_info_df[self.ft_io_info_df['ref_clk_period'] == self.ft_io_info_df['tar_clk_period']]

    def iterateFtPath(self, start_instterm, series=None, verbose=False) -> List[pd.Series]:
        if series in None:
            series = []
        try:
            current_row = self.ft_raw_io_info_df.loc[start_instterm]
        except KeyError:
            return []
        series.append(current_row)
        next_instterm = current_row['tar_instterm_name']
        next_inst = os.path.dirname(next_instterm)
        next_reg = current_row['tar_reg_name']

        if verbose:
            Print(start_instterm)
            Print(next_instterm)

        if next_reg.startwith('port-'):
            return self.iterateFtPath(next_inst + '/' + next_reg.replace('port-', ''), series, verbose)
        else:
            return series

    def __classifyRegularIoInfo(self):
        Print(f'Classify regular interface info by clock domain and module2module pair')
        for clk_tuple, clk_df in self.regular_io_info_df.groupby(['ref_clk_name', 'ref_clk_period']):
            self.regular_io_info_df[clk_tuple] = {'df': clk_df, 'uniq_df': clk_df.drop(['ref_instterm_name', 'tar_instterm_name'], axis=1).drop_duplicates(igonre_index=True),
                                                  'module_pairs': {}}
            for pair, pair_df in clk_df.groupby(['ref_module', 'tar_module']):
                self.regular_io_info_dict[clk_tuple]['module_pairs'][pair] = {'df': pair_df}

    def genFeedthroughReport(self, out_dir='ft_interface_info_rpts', target_clock_domains=None, targer_module_pair=None):
        Print(f'Start to generate report to {out_dir}')
        for clk in self.ft_io_info_df:
            if target_clock_domains and clk not in target_clock_domains:
                continue
            Print(f'Generate report for clock domain {clk}')
            self.__writeRpts(self.ft_io_info_dict[clk]['df'], f'{out_dir}/{clk[0]}_{clk[1]}')
            for pair in self.ft_io_info_dict[clk]['module_pairs']:
                if target_clock_domains and pair not in targer_module_pair:
                    continue
                Print(f'  Generate report for module pair {pair}')
                df = self.ft_io_info_dict[clk]['module_pair'][pair]['df']
                self.__writeRpts(df, f'{out_dir}/{clk[0]}_{clk[1]}/module_pairs/{pair[0]}.{pair[1]}', True)

    def genRegularReport(self, out_dir='regular_interface_info_rpts', target_clock_domains=None, targer_module_pair=None):
        Print(f'Start to generate report to {out_dir}')
        for clk in self.regular_io_info_df:
            if target_clock_domains and clk not in target_clock_domains:
                continue
            Print(f'Generate report for clock domain {clk}')
            self.__writeRpts(self.regular_io_info_dict[clk]['df'], f'{out_dir}/{clk[0]}_{clk[1]}')
            for pair in self.regular_io_info_df[clk]['module_pairs']:
                if target_clock_domains and pair not in targer_module_pair:
                    continue
                Print(f'  Generate report for module pair {pair}')
                df = self.regular_io_info_dict[clk]['module_pair'][pair]['df']
                self.__writeRpts(df, f'{out_dir}/{clk[0]}_{clk[1]}/module_pairs/{pair[0]}.{pair[1]}', True)

    def __writeRpts(self, df: pd.DataFrame, out_dir: str, enable_detail=False):
        os.system(f'mdkir -p {out_dir}')
        self.__summaryReport(df, out_dir)
        self.__distPlot(df, out_dir)
        self.__delayPlot(df, out_dir)
        self.__slackPlot(df, out_dir)
        if enable_detail is True:
            self.__detailReport(df, out_dir)

    def __distPlot(self, df: pd.DataFrame, out_dir: str):
        file_name = f'{out_dir}/dist.png'
        _df = df.sort_values('total_manhattan_distance', ascending=False, ignore_index=True)
        plt.figure(figsize=(10, 7.5))
        plt.plot(_df[f'total_manhattan_distance'], label='total_dist')
        plt.plot(_df[f'ref_manhattan_distance'], label='ref_dist')
        plt.plot(_df[f'tar_manhattan_distance'], label='tar_dist')
        plt.title('Manhanttan Distance')
        plt.xlabel('io pair index')
        plt.ylabel('distance(um)')
        plt.legend()
        plt.grid()
        plt.savefig(file_name)
        plt.close()
        _df.to_csv(f'{out_dir}/io_info.sorted_by_dist.csv', index=False)

    def __delayPlot(self, df: pd.DataFrame, out_dir: str):
        file_name = f'{out_dir}/delay.png'
        _df = df.sort_values('total_path_delay', ascending=False, ignore_index=True)
        plt.figure(figsize=(10, 7.5))
        plt.plot(_df[f'total_path_delay'], label='total_delay')
        plt.plot(_df[f'ref_path_delay'], label='ref_delay')
        plt.plot(_df[f'tar_path_delay'], label='tar_delay')
        plt.title('Path Delay')
        plt.xlabel('io pair index')
        plt.ylabel('delay(ns)')
        plt.legend()
        plt.grid()
        plt.savefig(file_name)
        plt.close()
        _df.to_csv(f'{out_dir}/io_info.sorted_by_delay.csv', index=False)

    def __slackPlot(self, df: pd.DataFrame, out_dir: str):
        file_name = f'{out_dir}/delay.png'
        _df = df.sort_values('setup_slack', ascending=False, ignore_index=True)
        plt.figure(figsize=(10, 7.5))
        plt.plot(_df[f'setup_slack'], label='setup_slack')
        plt.title('Setup Slack')
        plt.xlabel('io pair index')
        plt.ylabel('slack(ns)')
        plt.legend()
        plt.grid()
        plt.savefig(file_name)
        plt.close()
        _df.to_csv(f'{out_dir}/io_info.sorted_by_slack.csv', index=False)

    def __summaryReport(self, df: pd.DataFrame, out_dir: str):
        file_name = f'{out_dir}/interface_info_summary.rpt'
        rd = 4
        content = []
        dist_series = df['total_manhanttan_distance']
        delay_series = df['total_path_delay']
        skew_series = df['skew']
        slack_series = df['setup_slack']

        content.append(f'Manhanttan distance(um): min: {round(dist_series.min(), rd):>10}, max: {round(dist_series.max(), rd):>10}, mean: {round(dist_series.mean(), rd):>10}')
        content.append(f'Path delay(ns):          min: {round(delay_series.min(), rd):>10}, max: {round(delay_series.max(), rd):>10}, mean: {round(delay_series.mean(), rd):>10}')
        content.append(f'skew(ns):                min: {round(skew_series.min(), rd):>10}, max: {round(skew_series.max(), rd):>10}, mean: {round(skew_series.mean(), rd):>10}')
        content.append(f'Setup slack(ns):         min: {round(slack_series.min(), rd):>10}, max: {round(slack_series.max(), rd):>10}, mean: {round(slack_series.mean(), rd):>10}')

        with open(file_name, 'w') as fh:
            for ii in content:
                fh.write(f'{ii}\n')

    def __detailReport(self, df: pd.DataFrame, out_dir: str):
        df = df.round(4)
        file_name = f'{out_dir}/interface_info_detail.rpt'
        if 'ft_path' in df.columns:
            with open(file_name, 'w') as fh:
                idx = 0
                for _, row in df.sort_values('total_path_delay', ascending=False).iterrows():
                    idx += 1
                    fh.write(f'Path {idx}: {row["ref_instterm_name"]} -> {row["tar_instterm_name"]}\n')
                    fh.write(f'  Total delay: {row["total_path_delay"]} Total dist: {row["total_manhattan_distance"]}\n')
                    fh.write(f'  {row["ref_reg_name"]}\n')
                    fh.write(f'    dist {row["ref_manhattan_distance"]} delay {row["ref_path_delay"]}\n')
                    fh.write(f'  {row["ref_instterm_name"]}\n')
                    for ii in row['ft_path']:
                        fh.write(f'  {ii[0]}\n')
                        fh.write(f'    dist {ii[2]} delay {ii[3]}\n')
                        fh.write(f'  {ii[1]}\n')
                    fh.write(f'  {row["tar_instterm_name"]}\n')
                    fh.write(f'    dist {row["tar_manhattan_distance"]} delay {row["tar_path_delay"]}\n')
                    fh.write(f'  {row["tar_reg_name"]}\n')
                    fh.write(f'\n')
        else:
            with open(file_name, 'w') as fh:
                idx = 0
                for _, row in df.sort_values('total_path_delay', ascending=False).iterrows():
                    idx += 1
                    fh.write(f'Path {idx}: {row["ref_port_name"]} -> {row["tar_port_name"]}\n')
                    fh.write(f'  Total delay: {row["total_path_delay"]} Total dist: {row["total_manhattan_distance"]}\n')
                    fh.write(f'  {row["ref_reg_name"]}\n')
                    fh.write(f'    dist {row["ref_manhattan_distance"]} delay {row["ref_path_delay"]}\n')
                    fh.write(f'  {row["ref_port_name"]}\n')
                    fh.write(f'  {row["tar_port_name"]}\n')
                    fh.write(f'    dist {row["tar_manhattan_distance"]} delay {row["tar_path_delay"]}\n')
                    fh.write(f'  {row["tar_reg_name"]}\n')
                    fh.write(f'\n')














