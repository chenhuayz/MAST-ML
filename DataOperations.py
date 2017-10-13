__author__ = 'Ryan Jacobs'

import pandas as pd
import logging
import sys
import numpy as np
import os
from matplotlib import pyplot
from MASTMLInitializer import ConfigFileParser

class DataParser(object):
    """Class to parse input csv file and create pandas dataframe, and extract features
    """
    def __init__(self, configdict=None):
        self.configdict = configdict

    def parse_fromfile(self, datapath, as_array=False):
        if self.configdict is not None:
            dataframe = self.import_data(datapath=datapath)
            x_features, y_feature = self.get_features(dataframe=dataframe, target_feature=None, from_input_file=True)
            #dataframe = DataframeUtilities()._assign_columns_as_features(dataframe=dataframe, x_features=x_features, y_feature=y_feature, column_names=column_names, remove_first_row=True)
            Xdata, ydata = self.get_data(dataframe=dataframe, x_features=x_features, y_feature=y_feature)

            if as_array == bool(True):
                Xdata = np.asarray(Xdata)
                ydata = np.asarray(ydata)
        else:
            raise OSError('You must specify a configdict as input to use the parse_fromfile method')

        return Xdata, ydata, x_features, y_feature, dataframe

    def parse_fromdataframe(self, dataframe, target_feature, as_array=False):
        x_features, y_feature = self.get_features(dataframe=dataframe, target_feature=target_feature, from_input_file=False)
        Xdata, ydata = self.get_data(dataframe=dataframe, x_features=x_features, y_feature=y_feature)

        if as_array == bool(True):
            Xdata = np.asarray(Xdata)
            ydata = np.asarray(ydata)

        return Xdata, ydata, x_features, y_feature, dataframe

    def import_data(self, datapath):
        try:
            dataframe = pd.read_csv(datapath, header=0)
            #column_names = dataframe.iloc[0].tolist()
        except IOError:
            logging.info('Error reading in your input data file, specify a valid path to your input data')
            sys.exit()
        return dataframe

    def get_features(self, dataframe, target_feature=None, from_input_file=False):
        if from_input_file == bool(True):
            y_feature_from_input = self.configdict['General Setup']['target_feature']

            x_and_y_features = dataframe.columns.values.tolist()
            if self.configdict['General Setup']['input_features'] == ['Auto'] or self.configdict['General Setup']['input_features'] == 'Auto':
                print('found auto')
                #x_and_y_features = dataframe.columns.values.tolist()
                x_features = []
                for feature in x_and_y_features:
                    if feature not in y_feature_from_input:
                        if 'grouping_feature' in self.configdict['General Setup'].keys():
                            if feature not in self.configdict['General Setup']['grouping_feature']:
                                x_features.append(feature)
                        else:
                            x_features.append(feature)
            else:
                x_features = [feature for feature in self.configdict['General Setup']['input_features']]

            for feature in x_and_y_features:
                if feature not in x_features:
                    if feature in y_feature_from_input:
                        y_feature = feature

            #print(y_feature, type(y_feature))

        elif from_input_file == bool(False):
            y_feature = target_feature
            if 'grouping_feature' in self.configdict['General Setup'].keys():
                x_features = [feature for feature in dataframe.columns.values if feature not in [y_feature, self.configdict['General Setup']['grouping_feature']]]
            else:
                x_features = [feature for feature in dataframe.columns.values if feature not in y_feature]

        return x_features, y_feature

    def get_data(self, dataframe, x_features, y_feature):
        Xdata = dataframe.loc[:, x_features]
        ydata = dataframe.loc[:, y_feature]
        return Xdata, ydata

class DataframeUtilities(object):
    """This class is a collection of basic utilities for dataframe manipulation, and exchanging between dataframes and numpy arrays
    """
    @classmethod
    def _merge_dataframe_columns(cls, dataframe1, dataframe2):
        dataframe = pd.concat([dataframe1, dataframe2], axis=1, join='outer')
        return dataframe

    @classmethod
    def _merge_dataframe_rows(cls, dataframe1, dataframe2):
        dataframe = pd.merge(left=dataframe1, right=dataframe2, how='outer')
        return dataframe

    @classmethod
    def _get_dataframe_statistics(cls, dataframe):
        return dataframe.describe(include='all')

    @classmethod
    def _dataframe_to_array(cls, dataframe):
        array = np.asarray(dataframe)
        return array

    @classmethod
    def _array_to_dataframe(cls, array):
        dataframe = pd.DataFrame(data=array, index=range(0, len(array)))
        return dataframe

    @classmethod
    def _concatenate_arrays(cls, X_array, y_array):
        array = np.concatenate((X_array, y_array), axis=1)
        return array

    @classmethod
    def _assign_columns_as_features(cls, dataframe, x_features, y_feature, remove_first_row=True):
        column_dict = {}
        x_and_y_features = [feature for feature in x_features]
        x_and_y_features.append(y_feature)
        for i, feature in enumerate(x_and_y_features):
            column_dict[i] = feature
        dataframe = dataframe.rename(columns=column_dict)
        if remove_first_row == bool(True):
            dataframe = dataframe.drop([0])  # Need to remove feature names from first row so can obtain data
        return dataframe

    @classmethod
    def _save_all_dataframe_statistics(cls, dataframe, data_path):
        dataframe_stats = cls._get_dataframe_statistics(dataframe=dataframe)
        # Need configdict to get save path
        configdict = ConfigFileParser(configfile=sys.argv[1]).get_config_dict(path_to_file=os.getcwd())
        data_path_name = data_path.split('./')[1]
        data_path_name = data_path_name.split('.csv')[0]
        dataframe_stats.to_csv(configdict['General Setup']['save_path'] + "/" + 'input_data_statistics_'+data_path_name+'.csv',index=True)
        return

    @classmethod
    def _plot_dataframe_histogram(cls, configdict, dataframe, y_feature):
        num_bins = round((dataframe.shape[0])/15, 0)
        if num_bins < 1:
            num_bins = 1
        pyplot.hist(x=dataframe[y_feature], bins=num_bins, edgecolor='k')
        pyplot.title('Histogram of ' + y_feature + ' values')
        pyplot.xlabel(y_feature + ' value')
        pyplot.ylabel('Occurrences in dataset')
        pyplot.savefig(configdict['General Setup']['save_path'] + "/" + 'input_data_histogram.pdf')
        return