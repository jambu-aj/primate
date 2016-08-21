__author__ = "jambu"

import numpy
import os
import time
import subprocess
import csv


class Ticker(object):
    """
    Object created for each .csv from Yahoo Finance
    """
    def __init__(self, csv_path):
        with open(csv_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            self.rows = [row for row in reader]

        # Parse CSV Path for Ticker Name and Time Period contained in csv
        csv_path_list = csv_path.split("/")
        keywords = csv_path_list[len(csv_path_list)-1].split("_")
        keywords[len(keywords)- 1] = keywords[-1:][0][:-4]
        self.name = keywords[0].upper()
        self.period = keywords[1].upper()

    def get_name(self):
        """
        Handler for getting name
        :return: self.name (Str)
        """
        return self.name

    def get_period(self):
        """
        Handler for getting time period
        :return: self.period (Str)
        """
        return self.period

    def get_rows(self):
        """
        Handler for getting all Rows as a List of row Dicts
        :return: self.rows (List of Dicts)
        """
        return self.rows

    def get_column_strings(self, column_name):
        """
        Returns column's data as a list with Column Name
        :param column_name: (Str)
        :return: values - list of column's data (List of Strings)
        """
        try:
            values = [row[column_name.title()] for row in self.rows]
            return values
        except KeyError as e:
            print "Invalid Column Name"

    def get_column_floats(self, column_name):
        """
        Returns column's data as a list with Column Name
        :param column_name: (Str)
        :return: values - list of column's data (List of Floats)
        """
        try:
            values = [float(row[column_name.title()]) for row in self.rows]
            return values
        except KeyError as e:
            print "Invalid Column Name"
    '''
    @staticmethod
    def get_all_rows(csv_):
        """
        Takes a CSV from the csv module handler and returns an array of rows
        :param csv_: CSV file (Reader Object)
        :return: array of rows (List of Lists)
        """
        a = []
        for row in csv_:
            a.append(row)
        return a

    @staticmethod
    def get_all_columns(arr):
        """
        Takes a List of Rows and Transposes to a List of Columns
        :param arr: Input List of Rows (List of Lists)
        :return: array of columns (List of Lists)
        """
        b = []
        a = []
        for idx in range(0, len(arr[0])):
            for row in arr:
                a.append(row[idx])
            b.append(a)
            a = []
        return b
    '''
