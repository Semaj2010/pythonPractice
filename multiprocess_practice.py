import multiprocessing

def consumer(input_q):
    while True:
        item = input_q.get()
        #
        print(item)
        #
        input_q.task_done()

def producer(sequence, output_q):
    for item in sequence:
        #
        output_q.put(item)


# setting
if __name__ == '__main__':
    q = multiprocessing.JoinableQueue()
    # start consumer process
    cons_p = multiprocessing.Process(target=consumer,args=(q,))
    cons_p.daemon=True
    cons_p.start()

    # create sequences
    sequence = [1,2,3,4]
    producer(sequence,q)
    
    q.join()

