import argparse
import muse
import okjob
import reed

from logger import logging

def main(command, reed_init_start, reed_init_end, reed_sleep_time):
    if command == 'init':
        logging.debug(f"{__file__}: Starting initial data retrieval")
        muse.get_all_source_data()
        okjob.get_all_source_data()
        reed. get_all_data_by_location(reed_init_start, reed_init_end, reed_sleep_time)
        logging.debug(f"{__file__}: Initial data retrieval complete")
        
    if command == 'update':
        logging.debug(f"{__file__}: Starting data retrieval update")
        muse.update_all_source_data()
        okjob.update_all_source_data()
        reed.update_all_source_data()
        logging.debug(f"{__file__}: Data retrieval update complete")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data retrieval tool that can perform initial data retrieval or an update ('init' or 'update')")
    parser.add_argument("command", choices=['init', 'update'], help="data retrieval, can either do the initial data retrieval or and update ('init' or 'update')")
    parser.add_argument("-s", "--start", dest="start_index", type=int, default=None, help="Start index for reed init")
    parser.add_argument("-e", "--end", dest="end_index", type=int, default=None, help="End index for reed init")
    parser.add_argument("-l", "--sleep", dest="sleep_time", type=int, default=60, help="Idle time for reed init")
    
    args = parser.parse_args()
    main(args.command, args.start_index, args.end_index, args.sleep_time)