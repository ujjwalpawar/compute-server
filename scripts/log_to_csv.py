#!/usr/bin/python
import os
import sys
import json
import pprint
from datetime import datetime
import csv
import numpy as np
from sklearn.impute import KNNImputer
import pandas as pd

# Import MobileInsight modules
from mobile_insight.monitor.dm_collector import dm_collector_c, DMLogPacket, FormatError

SUPPORTED_TYPES = list(dm_collector_c.log_packet_types)

SAMSUNG_ATTRIBUTE_LIST = [  'LTE_MAC_DL_Transport_Block(->)Subpackets(->)Samples(->)Cell Id',
                            'LTE_MAC_DL_Transport_Block(->)Subpackets(->)Samples(->)DL TBS (bytes)',
                            'LTE_MAC_Rach_Attempt(->)Subpackets(->)Cell Id',
                            'LTE_MAC_Rach_Attempt(->)Subpackets(->)Msg1(->)Preamble power offset',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Cells(->)Cell Id',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Cells(->)Contention resolution timer (ms)',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Cells(->)Delta preamble Msg3',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Cells(->)Max retx Msg3',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Cells(->)PMax (dBm)',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Cells(->)Power offset Group_B',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Cells(->)Power ramping step (dB)',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Cells(->)Preamble initial power (dB)',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Cells(->)Preamble trans max',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Num Active Cells',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)PMax (dBm)',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Power offset Group_B',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Power ramping step (dB)',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Preamble initial power (dB)',
                            'LTE_MAC_Rach_Trigger(->)Subpackets(->)Preamble trans max',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)Detected Cells',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)Detected Cells(->)Physical Cell ID',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)Neighbor Cells(->)Physical Cell ID',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)Neighbor Cells(->)RSRP(dBm)',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)Neighbor Cells(->)RSRQ(dB)',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)Number of Detected Cells',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)Number of Neighbor Cells',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)RSRP(dBm)',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)RSRQ(dB)',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)Serving Cell Index',
                            'LTE_PHY_Connected_Mode_Intra_Freq_Meas(->)Serving Physical Cell ID',
                            'LTE_PHY_Idle_Neighbor_Cell_Meas(->)SubPackets(->)Neighbor Cells(->)Cell ID',
                            'LTE_PHY_Idle_Neighbor_Cell_Meas(->)SubPackets(->)Neighbor Cells(->)Enabled Tx Antennas',
                            'LTE_PHY_Idle_Neighbor_Cell_Meas(->)SubPackets(->)Num Cells',
                            'LTE_PHY_Idle_Neighbor_Cell_Meas(->)SubPackets(->)Num Rx Ant',
                            'LTE_PHY_PDCCH_Decoding_Result(->)Band Width (MHz)',
                            'LTE_PHY_PDCCH_Decoding_Result(->)Num eNB Antennas',
                            'LTE_PHY_PDSCH_Decoding_Result(->)Records(->)Number of Streams',
                            'LTE_PHY_PDSCH_Decoding_Result(->)Serving Cell ID',
                            'LTE_PHY_PDSCH_Packet(->)Frequency Selective PMI',
                            'LTE_PHY_PDSCH_Packet(->)MCS 0',
                            'LTE_PHY_PDSCH_Packet(->)MCS 1',
                            'LTE_PHY_PDSCH_Packet(->)Number of Rx Antennas(N)',
                            'LTE_PHY_PDSCH_Packet(->)Number of Tx Antennas(M)',
                            'LTE_PHY_PDSCH_Packet(->)PMI Index',
                            'LTE_PHY_PDSCH_Packet(->)RB Allocation Slot 0[0]',
                            'LTE_PHY_PDSCH_Packet(->)RB Allocation Slot 0[1]',
                            'LTE_PHY_PDSCH_Packet(->)RB Allocation Slot 1[0]',
                            'LTE_PHY_PDSCH_Packet(->)RB Allocation Slot 1[1]',
                            'LTE_PHY_PDSCH_Packet(->)Serving Cell ID',
                            'LTE_PHY_PDSCH_Packet(->)Spatial Rank',
                            'LTE_PHY_PDSCH_Packet(->)TBS 0',
                            'LTE_PHY_PDSCH_Packet(->)TBS 1',
                            'LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Num Layers',
                            'LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Num RBs',
                            'LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Num Transport Blocks Present',
                            'LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Serving Cell Index',
                            'LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Transport Blocks(->)ACK/NACK Decision',
                            'LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Transport Blocks(->)MCS',
                            'LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Transport Blocks(->)Modulation Type',
                            'LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Transport Blocks(->)Num RBs',
                            'LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Transport Blocks(->)TB Size',
                            'LTE_PHY_PUCCH_CSF(->)Alt Cqi Table Data',
                            'LTE_PHY_PUCCH_CSF(->)CQI CW0',
                            'LTE_PHY_PUCCH_CSF(->)CQI CW1',
                            'LTE_PHY_PUCCH_CSF(->)Rank Index',
                            'LTE_PHY_PUCCH_CSF(->)Size BWP',
                            'LTE_PHY_PUCCH_CSF(->)Wideband PMI',
                            'LTE_PHY_PUCCH_CSF(->)Wideband PMI1',
                            'LTE_PHY_PUSCH_CSF(->)Num CSIrs Ports',
                            'LTE_PHY_PUSCH_CSF(->)Number of Subbands',
                            'LTE_PHY_PUSCH_CSF(->)Rank Index',
                            'LTE_PHY_PUSCH_CSF(->)Single MB PMI',
                            'LTE_PHY_PUSCH_CSF(->)Single WB PMI',
                            'LTE_PHY_PUSCH_CSF(->)WideBand CQI CW0',
                            'LTE_PHY_PUSCH_CSF(->)WideBand CQI CW1',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)ACK',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)Coding Rate',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)Coding Rate Data',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)CQI',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)Num of RB',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)Num RB Cluster1',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)PUSCH Digital Gain (dB)',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)PUSCH Mod Order',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)PUSCH TB Size',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)PUSCH Tx Power (dBm)',
                            'LTE_PHY_PUSCH_Tx_Report(->)Records(->)RI',
                            'LTE_PHY_PUSCH_Tx_Report(->)Serving Cell ID',
                            'LTE_PHY_RLM_Report(->)Records(->)In Sync BLER (%)',
                            'LTE_PHY_RLM_Report(->)Records(->)In Sync Count',
                            'LTE_PHY_RLM_Report(->)Records(->)Out of Sync BLER (%)',
                            'LTE_PHY_RLM_Report(->)Records(->)Out of Sync Count',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)FTL SNR Rx[0]',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)FTL SNR Rx[1]',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)Num-of-cells',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)Physical Cell ID',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)RSRP',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)RSRP Rx[0]',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)RSRP Rx[1]',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)RSRQ',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)RSRQ Rx[0]',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)RSRQ Rx[1]',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)RSSI',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)RSSI Rx[0]',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)RSSI Rx[1]',
                            'LTE_PHY_Serv_Cell_Measurement(->)Subpackets(->)Serving Cell Index',
                            'LTE_RRC_MIB_Packet(->)DL BW',
                            'LTE_RRC_MIB_Packet(->)Freq',
                            'LTE_RRC_MIB_Packet(->)Number of Antenna',
                            'LTE_RRC_MIB_Packet(->)Physical Cell ID',
                            'LTE_RRC_Serv_Cell_Info(->)Band Indicator',
                            'LTE_RRC_Serv_Cell_Info(->)Cell ID',
                            'LTE_RRC_Serv_Cell_Info(->)Cell Identity',
                            'LTE_RRC_Serv_Cell_Info(->)Downlink bandwidth',
                            'LTE_RRC_Serv_Cell_Info(->)Downlink frequency',
                            'LTE_RRC_Serv_Cell_Info(->)Uplink bandwidth',
                            'LTE_RRC_Serv_Cell_Info(->)Uplink frequency',
                            'timestamp']

SAMSUNG_CATEGORICAL_ATTRIBUTES = ["LTE_PHY_PDSCH_Packet(->)Frequency Selective PMI",
                            "LTE_PHY_PDSCH_Packet(->)MCS 0",
                            "LTE_PHY_PDSCH_Packet(->)MCS 1",
                            "LTE_PHY_PDSCH_Packet(->)RB Allocation Slot 0[0]",
                            "LTE_PHY_PDSCH_Packet(->)RB Allocation Slot 0[1]",
                            "LTE_PHY_PDSCH_Packet(->)RB Allocation Slot 1[0]",
                            "LTE_PHY_PDSCH_Packet(->)RB Allocation Slot 1[1]",
                            "LTE_PHY_PDSCH_Packet(->)Spatial Rank", 
                            "LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Transport Blocks(->)ACK/NACK Decision",
                            "LTE_PHY_PDSCH_Stat_Indication(->)Records(->)Transport Blocks(->)Modulation Type",
                            "LTE_PHY_PUCCH_CSF(->)Rank Index",
                            "LTE_PHY_PUSCH_CSF(->)Rank Index",
                            "LTE_PHY_PUSCH_Tx_Report(->)Records(->)ACK",
                            "LTE_PHY_PUSCH_Tx_Report(->)Records(->)CQI",
                            "LTE_PHY_PUSCH_Tx_Report(->)Records(->)PUSCH Mod Order",
                            "LTE_PHY_PUSCH_Tx_Report(->)Records(->)RI",
                            "LTE_RRC_MIB_Packet(->)DL BW",
                            "LTE_RRC_Serv_Cell_Info(->)Downlink bandwidth",
                            "LTE_RRC_Serv_Cell_Info(->)Uplink bandwidth"
]


def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

def AnalyzeLog(log_path, messages):
    input_file = open(log_path, "rb")
    dm_collector_c.reset()

    dm_collector_c.set_filtered(SUPPORTED_TYPES)
    while True:
        s = input_file.read(64)
        if s:
            dm_collector_c.feed_binary(s)
            decoded = dm_collector_c.receive_log_packet(False, True)

        if not s:
            break

        if decoded:
            try:
                packet = DMLogPacket(decoded[0])
                type_id = packet.get_type_id()
                if type_id != 'Modem_debug_message':
                    decoded_msg = packet.decode_json()
                    json_obj = json.loads(decoded_msg)
                    messages.append(json_obj)
            except:
                continue

    input_file.close()

def flatDictionary(dictionary, prefix, plain_dictionary):
    for k, v in dictionary.items():
        if isinstance(v, list) and v:
            flatDictionary(v[0], prefix+'(->)'+str(k), plain_dictionary) # Only the first element of the list is included
        elif isinstance(v, dict):
            flatDictionary(v, prefix+'(->)'+str(k), plain_dictionary)
        else:
            plain_dictionary[prefix+'(->)'+str(k)] = v

def mergeMessageHeaders(flat_messages):
    headers = set()
    for msg in flat_messages:
        for k, v in msg.items():
            words = k.split('(->)')
            if len(words) == 2 and words[1] in ['log_msg_len', 'type_id', 'timestamp', 'Version']:
                headers.add(words[1])
            else:
                headers.add(k)

    return list(headers)


def tableToCSV(output_path, table):
    with open(output_path, 'w') as f: 
        write = csv.writer(f)
        write.writerows(table)

def findPrev(col, pos):
    for i in range(pos, 0, -1):
        if not isinstance(col[i], float):
            return i
    return -1;

def findNext(col, pos, maximum):
    for i in range(pos, maximum):
        if not isinstance(col[i], float):
            return i
    return -1


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("USE: python3 mi2log_dump.py <Log File (.mi2log)> <Output File (.csv)>")
        sys.exit()

    messages = []
    flat_messages = []

    blockPrint()
    AnalyzeLog(sys.argv[1], messages)
    enablePrint()

    for msg in messages:
        msg_dict = dict()
        flatDictionary(msg, msg['type_id'], msg_dict)
        flat_messages.append(msg_dict)

    headers = mergeMessageHeaders(flat_messages)
    # Get the intersection between the header list and the Samsung attribute list
    filtered_headers = list(set(headers).intersection(SAMSUNG_ATTRIBUTE_LIST))
    filtered_headers.sort() # The set usage produce randomly ordered header lists

    num_colums = len(filtered_headers)
    num_messages = 0

    table = [filtered_headers, ]

    for msg in flat_messages:
        row = [np.nan,]*num_colums
        for k, v in msg.items():
            words = k.split('(->)')
            if len(words) == 2 and words[1] == 'timestamp': # Special case to get the timestamp as float
                try:
                    date_obj = datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')
                except:
                    date_obj = datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                row[filtered_headers.index(words[1])] = float(date_obj.timestamp())
            elif len(words) == 2 and words[1] in ['log_msg_len', 'type_id', 'Version']:
                try:
                    row[filtered_headers.index(words[1])] = v
                except ValueError:
                    pass
            else:
                try:
                    row[filtered_headers.index(k)] = v
                except ValueError:
                    pass
        if row.count(np.nan) < num_colums - 1:
            table.append(row)
            num_messages += 1

    stats = []
    for i in range(num_colums):
        counter = 0
        for row in table[1:]:
            if isinstance(row[i], float) and np.isnan(row[i]):
                counter += 1
        stats.append((counter/num_messages) * 100)
    np_stats = np.array(stats)
    # Dump some statistics
    print('Number of messages: ', num_messages)
    print('Number of attributes: ', num_colums)
    print('Max: ', np.amax(np_stats))
    print('Min: ', np.amin(np_stats))
    print('Mean: ', np.mean(np_stats))
    print('Median: ', np.median(np_stats))
    print('Std: ', np.std(np_stats))

    pd_table = pd.DataFrame(table[1:], columns=table[0])

    #create two DataFrames, one for each data type
    data_numeric = pd_table.select_dtypes(exclude='object')
    data_categorical = pd_table.select_dtypes(include='object')

    # Impute only numeric columns
    imputer = KNNImputer(n_neighbors=2, missing_values=np.nan, weights='uniform', copy=False)
    imputer.fit_transform(data_numeric)

    print('Numerical attributes imputed')

    # Apply imputation on categorical columns (KNN based on timestamp)
    data_categorical_copy = data_categorical.copy()
    for cat_attr in SAMSUNG_CATEGORICAL_ATTRIBUTES:
        try:
            for i, elem in enumerate(data_categorical_copy[cat_attr]):
                if isinstance(elem, float) and np.isnan(elem): # If it is np.nan
                    prev_ind = findPrev(data_categorical_copy[cat_attr], i)
                    next_ind = findNext(data_categorical_copy[cat_attr], i, len(data_categorical_copy[cat_attr]))
                    if prev_ind == -1 and next_ind != -1: # No previous element
                        data_categorical[cat_attr][i] = data_categorical[cat_attr][next_ind]
                    elif prev_ind != -1 and next_ind == -1: # No next element
                        data_categorical[cat_attr][i] = data_categorical[cat_attr][prev_ind]
                    elif prev_ind != -1 and next_ind != -1:
                        # Choose the closest element (timestamp based)
                        current_ts = pd_table['timestamp'][i]
                        prev_ts = pd_table['timestamp'][prev_ind]
                        next_ts = pd_table['timestamp'][next_ind]
                        if current_ts-prev_ts <= next_ts-current_ts: # Prev
                            data_categorical[cat_attr][i] = data_categorical[cat_attr][prev_ind]
                        else: # Next
                            data_categorical[cat_attr][i] = data_categorical[cat_attr][next_ind]
        except KeyError:
            print(cat_attr, 'is not included in the log file')

    print('Categorical attributes imputed')

    # Merge numeric and categoric columns
    imputed_table = pd.concat([data_numeric, data_categorical], axis = 1)

    imputed_table.to_csv(sys.argv[2])


