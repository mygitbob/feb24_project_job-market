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
    # max page number is 99, this means we can get 100 * 20 = 2000 results
    muse.get_pages(10)
    # get 150 job entries from okjob
    # TODO: I have to check how we can get max results
    okjob.get_entries(200)
    # get as many as we can 
    # one call islimited to 100 results, we can get more data if we use "resultsToSkip" : x
    # then we can the next 100 results after x, for example get_entires(parameters={"resultsToSkip":"100"})
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