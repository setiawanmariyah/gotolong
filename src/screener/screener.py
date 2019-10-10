#!/usr/bin/python

import sys
import re
import csv
import traceback
import operator
import cutil.cutil
import finratio.comp_perf
import finratio.comp_price

from isin.isin import *
from amfi.amfi import *


# class Screener(Isin):
class Screener(Isin, Amfi):
    def __init__(self):
        super(Screener, self).__init__()
        self.sc_ratio_values = {}
        self.sc_nsecode = []
        self.sc_nsecode_industry = {} 
        # margin of safety
        self.debug_level = 0
        self.sc_ratio_name = {'Name': 'name',
                              'BSE Code': 'bse_code', 'NSE Code': 'nse_code', 'Industry': 'industry',
                              'Current Price': 'cmp',
                              'Market Capitalization': 'mcap',
                              'Sales': 'sales', 'Net profit': 'np',
                              'Price to Earning': 'pe', 'Historical PE 5Years': 'pe5',
                              'EPS 12M Rs.': 'eps', 'PEG Ratio': 'peg', 'Price to book value': 'p2bv',
                              'CMP / OCF': 'p2ocf',
                              'Price to Sales': 'p2sales', 'EVEBITDA': 'ev2ebitda', 'Enterprise Value': 'ev',
                              'OPM': 'opm', 'Debt to equity': 'd2e', 'Int Coverage': 'ic',
                              'Dividend Payout Ratio': 'dp',
                              'Average dividend payout 3years': 'dp3', 'Dividend yield': 'dy',
                              'Average return on equity 3Years': 'roe3',
                              'ROCE3yr avg': 'roce3', 'Current ratio': 'cr', 'Sales growth 5Years': 'sales5',
                              'Profit growth 5Years': 'profit5', 'Pledged percentage': 'pledge',
                              'Promoter Holding': 'prom_hold',
                              'Piotroski score': 'piotski'}
        self.sc_ratio_loc = {'name': -1, 'bse_code': -1, 'nse_code': -1, 'industry': -1, 'captype': -1,
                             'cmp': -1, 'mcap': -1, 'sales': -1, 'np': -1,
                             'd2e': -1, 'roe3': -1, 'roce3': -1, 'dp3': -1, 'dp': -1, 'dy': -1,
                             'pe': -1, 'pe5': -1, 'peg': -1, 'p2bv': -1,
                             'p2sales': -1, 'ev2ebitda': -1, 'ev': -1, 'opm': -1,
                             'cr': -1, 'sales5': -1, 'profit5': -1, 'pledge': -1, 'piotski': -1}

    def set_debug_level(self, debug_level):
        self.debug_level = debug_level

    def load_screener_row(self, row):
        try:
            row_list = row
            if len(row_list) == 0:
                if self.debug_level > 1:
                    print('ignored empty row', row_list)
                return

            sc_name = row_list[0].strip()
            if sc_name == 'Name':
                if self.debug_level > 1:
                    print('picked up keys', row_list)
                ratio_name_column_index = 0
                for ratio in row_list:
                    if ratio in self.sc_ratio_name.keys():
                        new_key = self.sc_ratio_name[ratio]
                        if self.debug_level > 0:
                            print('found ratio', ratio, 'mapped to ', new_key)
                        self.sc_ratio_loc[new_key] = ratio_name_column_index
                    else:
                        print('check sc_ratio_name for ', ratio)
                    # increment the ratio name index
                    ratio_name_column_index += 1

                # don't try to delete and iterate original dictionary at the same time. it will become inconsistent.
                loc_dup = dict(self.sc_ratio_loc)
                # delete columns that doesn't have values 
                for ratio in loc_dup:
                    if loc_dup[ratio] == -1 and ratio != 'captype':
                        # remove the ratio name from original dictionary
                        self.sc_ratio_loc.pop(ratio)
                        if self.debug_level > 0:
                            print('removed ratio', ratio)
                    else:
                        if self.debug_level > 0:
                            print('kept ratio', ratio)
                return
            else:
                sc_nsecode = row_list[self.sc_ratio_loc['nse_code']]
                self.sc_nsecode.append(sc_nsecode)

                for ratio in self.sc_ratio_loc:
                    if ratio == 'captype':
                        self.sc_ratio_values[sc_nsecode, ratio] = self.get_amfi_captype_by_ticker(sc_nsecode)
                    else:
                        ratio_value = row_list[self.sc_ratio_loc[ratio]]
                        if ratio == 'industry':
                            self.sc_nsecode_industry[sc_nsecode] = ratio_value
                        self.sc_ratio_values[sc_nsecode, ratio] = ratio_value
                    if self.debug_level > 1:
                        print('ticker: ', sc_nsecode, 'ratio: ', ratio, 'value: ',
                              self.sc_ratio_values[sc_nsecode, ratio])


        except IndexError:
            print('except ', row)
            traceback.print_exc()
        except KeyError:
            print('except ', row)
            traceback.print_exc()
        except:
            print('except ', row)
            traceback.print_exc()

    def load_isin_data_both(self, isin_bse_filename, isin_nse_filename):
        # self.load_isin_bse_data(isin_bse_filename)
        # self.load_isin_nse_data(isin_nse_filename)
        self.load_isin_db()

    def load_screener_data(self, sc_filename):
        with open(sc_filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.load_screener_row(row)

    def print_phase1(self, out_filename, filter_rows=False):
        fh = open(out_filename, "w")
        for ratio in self.sc_ratio_loc:
            fh.write(ratio)
            fh.write(', ')
        fh.write('\n')

        if filter_rows:
            sorted_input = sorted(self.sc_nsecode_industry, key=self.sc_nsecode_industry.__getitem__)
        else:
            sorted_input = sorted(self.sc_nsecode)

        for sc_nsecode in sorted_input:
            skip_row = False
            p_str = ''
            for ratio in self.sc_ratio_loc:
                if filter_rows == True:
                    if ratio == 'd2e' or ratio == 'dp3' or ratio == 'roce3':
                        value = self.sc_ratio_values[sc_nsecode, ratio]
                        if value == '':
                            if self.debug_level > 1:
                                print(sc_nsecode, ' skipped ', ratio, 'due to missing value : ', value)
                            skip_row = True
                        else:
                            value = float(value)
                            if ratio == 'd2e' and value > 0.10:
                                if self.debug_level > 1:
                                    print(sc_nsecode, ' skipped due to d2e : ', value)
                                skip_row = True
                            if ratio == 'dp3' and value < 10:
                                if self.debug_level > 1:
                                    print(sc_nsecode, ' skipped due to dp3 : ', value)
                                skip_row = True
                            if ratio == 'roce3' and value < 10:
                                if self.debug_level > 1:
                                    print(sc_nsecode, ' skipped due to roce3 : ', value)
                                skip_row = True
                p_str += self.sc_ratio_values[sc_nsecode, ratio]
                p_str += ', '
            if skip_row == False:
                fh.write(p_str)
                fh.write('\n')
            
        fh.close()

    def print_phase2(self, out_filename):
        self.print_phase1(out_filename, True)