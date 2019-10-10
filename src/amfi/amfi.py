#!/usr/bin/python

import sys
import re
import csv
import traceback
import operator

import sqlite3

import cutil.cutil

from database.database import *

class Amfi(Database):
    def __init__(self):
        super(Amfi, self).__init__()
        # isin number
        self.amfi_isin_list = []
        self.amfi_ticker_list = []
        # serial number
        self.amfi_cname = {}
        self.amfi_mcap = {}
        self.amfi_rank = {}
        self.amfi_captype = {}
        self.amfi_ticker_isin_dict = {}
        self.amfi_isin_ticker_dict = {}
        self.debug_level = 0

    def set_debug_level(self, debug_level):
        self.debug_level = debug_level

    def load_amfi_row(self, row):
        try:
            row_list = row
            if len(row_list) == 0:
                print('ignored empty row', row_list)
                return

            serial_number = row_list[0]
            if serial_number == 'Sr. No.':
                if self.debug_level > 0:
                    print('skipped header line', row_list)
                return

            serial_number = cutil.cutil.get_number(serial_number)

            comp_name = row_list[1]
            isin_number = row_list[2]
            comp_ticker = row_list[3].upper().strip()
            if comp_ticker == '':
                comp_ticker = row_list[5]
            avg_mcap = cutil.cutil.get_number(row_list[9])
            captype = row_list[10].strip()
            if captype == 'Small Cap':
                if serial_number > 500 and serial_number < 750:
                    captype = 'Micro Cap'
                if serial_number > 750 and serial_number < 1000:
                    captype = 'Nano Cap'
                if serial_number > 1000:
                    captype = 'Unknown Cap'

            comp_name = cutil.cutil.normalize_comp_name(comp_name)

            if self.debug_level > 1:
                print('serial_number : ', serial_number )
                print('isin_number: ', isin_number)
                print('comp_ticker : ', comp_ticker)
                print('avg_mcap : ', avg_mcap )
                print('captype : ', captype )
                print('comp_name : ', comp_name)

            self.amfi_isin_ticker_dict[isin_number] = comp_ticker
            self.amfi_ticker_isin_dict[comp_ticker] = isin_number
            self.amfi_rank[comp_ticker] = serial_number
            self.amfi_cname[comp_ticker] = comp_name
            self.amfi_mcap[comp_ticker] = avg_mcap
            self.amfi_captype[comp_ticker] = captype
            self.amfi_isin_list.append(isin_number)
            self.amfi_ticker_list.append(comp_ticker)

            if self.debug_level > 1:
                print('comp_name : ', comp_name , '\n')
                print('isin_number: ', isin_number, '\n')

        except IndexError:
            print('except ', row)
        except:
            print('except ', row)
            traceback.print_exc()

    def load_amfi_data(self, in_filename):
        table = "amfi"
        # row_count = self.count_amfi_db(table)
        row_count = self.db_table_count_rows(table)
        if row_count == 0:
            self.insert_amfi_data(in_filename)
        else:
            print('amfi data already loaded in db', row_count)
        print('display db data')
        self.load_amfi_db()

    def insert_amfi_data(self, in_filename):
        SQL = """insert into amfi (sno, company_name, isin, bse_symbol, bse_mcap, nse_symbol, nse_mcap, mse_symbol, mse_mcap, avg_mcap, cap_type, unused1, unused2) values (:sno, :company_name, :isin, :bse_symbol, :bse_mcap, :nse_symbol, :nse_mcap, :mse_symbol, :mse_mcap, :avg_mcap, :cap_type, :unused1, :unused2) """
        cursor = self.db_conn.cursor()
        with open(in_filename, 'rt') as csvfile:
            # future
            csv_reader = csv.reader(csvfile)
            # insert row
            cursor.executemany(SQL, csv_reader)
            # commit db changes
            self.db_conn.commit()

    def load_amfi_db(self):
        table = "amfi"
        cursor = self.db_table_load(table)
        for row in cursor.fetchall():
            if self.debug_level > 1 :
                print(row)
            self.load_amfi_row(row)

    def print_phase1(self, out_filename):
        if self.debug_level > 0:
            print('output filename ', out_filename)
        fh = open(out_filename, "w")
        fh.write('amfi_rank, amfi_cname, amfi_isin, amfi_ticker, amfi_mcap, amfi_captype\n')
        for ticker in sorted(self.amfi_rank, key=self.amfi_rank.__getitem__):
            if self.debug_level > 1:
                print('isin ', ticker)
            p_str = str(self.amfi_rank[ticker])
            p_str += ', '
            p_str += self.amfi_cname[ticker]
            p_str += ', '
            p_str += self.amfi_ticker_isin_dict[ticker]
            p_str += ', '
            p_str += ticker
            p_str += ', '
            p_str += str(self.amfi_mcap[ticker])
            p_str += ', '
            p_str += self.amfi_captype[ticker]
            p_str += '\n'
            fh.write(p_str);
        fh.close()

    def amfi_get_isin_by_name(self, req_name):
        req_name = re.sub('\s+', ' ', req_name).strip()
        for amfi_isin in sorted(self.amfi_cname):
            # try to find a matching company
            comp_name = self.amfi_cname[amfi_isin]
            comp_name = comp_name.strip()
            if re.match(req_name, comp_name):
                if self.debug_level > 1:
                    print('found match : name : ', req_name)
                return amfi_isin
            if amfi_isin in  self.amfi_ticker:
                ticker_symbol = self.amfi_isin_ticker_dict[amfi_isin]
                if req_name.upper() == ticker_symbol :
                    if self.debug_level > 1:
                        print('found ticker : ', req_name)
                    return amfi_isin
        if self.debug_level > 1:
            print('amfi : comp not found : req_name :',req_name,':')
        return ''

    def amfi_get_value_by_isin(self, isin, value_name):
        try:
            ticker = self.amfi_isin_ticker_dict[isin]
            if ticker:
                self.amfi_get_value_by_ticker(self, isin, value_name)
        except KeyError:
            print('KeyError ', isin)
            traceback.print_exc()
        return 'UNK_COMP_2'

    def amfi_get_value_by_ticker(self, ticker, value_name):
        try:
            if ticker:
                if value_name == "cname":
                    return self.amfi_cname[ticker]
                if value_name == "mcap":
                    return self.amfi_mcap[ticker]
                if value_name == "rank":
                    return self.amfi_rank[ticker]
                if value_name == "captype":
                    return self.amfi_captype[ticker]
                if value_name == "isin":
                    return self.amfi_get_isin_by_ticker(ticker)
        except KeyError:
            print('KeyError ', ticker)
            traceback.print_exc()
        except:
            print('Except ', ticker)
            traceback.print_exc()
        if value_name == "mcap" or value_name == "rank":
            return 0
        else:
            return 'UNK_COMP_E'

    def amfi_get_ticker_by_isin(self, amfi_isin):
        if amfi_isin in self.amfi_ticker:
            return self.amfi_isin_ticker_dict[amfi_isin]
        return 'UNK_TICKER'

    def amfi_get_isin_by_ticker(self, ticker):
        try:
            amfi_isin = self.amfi_ticker_isin_dict[ticker]
            if amfi_isin:
                return amfi_isin
        except KeyError:
            print('KeyError ', ticker)
            traceback.print_exc()
        return 'UNK_ISIN'
