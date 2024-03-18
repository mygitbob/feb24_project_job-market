import muse
import okjob
from constants import Constants
import logger

# TODO: make functions async

def run():
    # log only errors
    logger.setup_logging(log_file=Constants.LOG_FILE, level=logger.logging.DEBUG)
    
    # delete previous collected raw data
    muse.remove_raw_data()
    okjob.remove_raw_data()

    # retrive data
    # get  pages 0 - 9 from muse
    muse.get_pages(10)
    # get 150 job entries from okjob
    okjob.get_entries(200)

    # process data & delete raw files
    muse.process_raw_data(delete_processed=False)
    okjob.proccess_raw_data(delete_processed=False)

    # merge processed data & delete single files
    muse.merge_processed_files(delete_source=True)
    okjob.merge_processed_files(delete_source=True)

if __name__ == "__main__":
    run()