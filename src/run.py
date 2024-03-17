import muse
import okjob
from constants import Constants
import logger

# TODO: make functions async

def run():
    # log only errors
    logger.setup_logging(log_file=Constants.LOG_FILE, level=logger.logging.DEBUG)
    
    # retrive data
    # get 20 pages from muse
    muse.save_raw_joblist(20)
    # get 150 job entries from okjob
    okjob.save_raw_joblist(end=151)

    # process data & delete raw files
    muse.process_raw_data(delete_processed=False)
    okjob.proccess_raw_data(delete_processed=False)

    # merge processed data & delete single files
    muse.merge_processed_files(delete_source=True)
    okjob.merge_processed_files(delete_source=True)

if __name__ == "__main__":
    run()