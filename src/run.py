import muse
import okjob

# TODO: make functions async

def run():
    # retrive data
    # get 20 pages from muse
    muse.save_raw_joblist(20)
    # get 150 job entries from okjob
    okjob.save_raw_joblist(end=151)

    #process data
    muse.proccess_raw_data()
    okjob.proccess_raw_data()

if __name__ == "__main__":
    run()