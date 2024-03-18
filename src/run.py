from constants import Constants
import logger
import muse
import okjob
import reed

# TODO: make functions async

def run():
    # log only errors
    logger.setup_logging(log_file=Constants.LOG_FILE, level=logger.logging.DEBUG)
    
    # delete previous collected raw data
    muse.remove_raw_data()
    okjob.remove_raw_data()
    reed.remove_raw_data()

    # retrive and save raw data
    # get  pages 0 - 9 from muse
    muse.get_pages(10)
    # get 150 job entries from okjob
    okjob.get_entries(200)
    # get as many as we can (this has to be improved)
    reed.get_entries()

    # process data & delete raw files
    muse.process_raw_data(delete_processed=True)
    okjob.proccess_raw_data(delete_processed=True)
    reed.proccess_raw_data(delete_processed=True)

    # merge processed data & delete single files
    muse.merge_processed_files(delete_source=True)
    okjob.merge_processed_files(delete_source=True)
    reed.merge_processed_files(delete_source=True)

if __name__ == "__main__":
    run()