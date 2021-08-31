import os, sys, argparse, \
        threading, json, math, socket


class Worker:
    # aggr_options is the aggressiveness, the key is the value passed in sys.argv
    # the value of each key build from [precent, timeout]
    # the precent is how many words to resolve in each loop
    # the timeout is how much time to wait between each loop\
    # you can change and tweak 
    aggr_options = {
        1: [10 / 100, 30],
        2: [30 / 100, 20],
        3: [50 / 100, 10],
        4: [80 / 100, 10],
        5: [95 / 100, 10]
    }

    def __init__(self, wrds, domain, aggressiveness, report_callback):
        self.wrds = wrds
        self.domain = domain
        self.aggressiveness = self.aggr_options[aggressiveness]
        self.wrds_per_loop = math.ceil(self.aggressiveness[0] * len(self.wrds))
        self.report_callback = report_callback


    def resolve(self, event):
        wrds_tracker = 0

        for i,wrd in enumerate(self.wrds):
            if i == self.wrds_per_loop:
                event.wait(self.aggressiveness[1])
                i = 0

            wrd = wrd.strip('\n')
            domain = f'{wrd}.{self.domain}'

            try:
                addr = socket.gethostbyname(domain)
            except: continue

            self.report_callback(domain, addr)


class WorkerManager:
    _threads = []

    def __init__(
        self, wrds, wrds_sum, wrds_per_thread, 
        domain, workers, json, output, time
    ):
        self.wrds = wrds
        self.wrds_sum = wrds_sum
        self.wrds_per_thread = wrds_per_thread
        self.domain  = domain
        self.workers = workers
        self.as_json = json
        self.output  = output
        self.time = time
        self._output = [] if self.as_json else ''

        self._event = threading.Event()
    
    def write(self, domain, addr):
        if self.as_json:
            self._output.append({domain: addr})
        else:
            out = f'{domain} => {addr}\n'
            self._output += out
            sys.stdout.write(out)
    
    def create_workers(self):
        wrds_tracker = 0
        
        for i in range(self.workers):
            worker_wrds = self.wrds[wrds_tracker:(wrds_tracker + self.wrds_per_thread)]
            
            if not worker_wrds: # mean there are no more words
                break

            worker = Worker(
                wrds=self.wrds[wrds_tracker:(wrds_tracker + self.wrds_per_thread)],
                domain=self.domain,
                aggressiveness=self.time,
                report_callback=self.write
            )
            thread = threading.Thread(target=worker.resolve, kwargs={'event': self._event})
            thread.daemon = False
            
            self._threads.append(thread)
            wrds_tracker += self.wrds_per_thread
    
    def work(self):
        if not self._threads:
            raise Exception('work called before create workers')

        for thread in self._threads:
            thread.start()
        self._check_alive()
    
    def _check_alive(self):
        while not all([not thread.is_alive() for thread in self._threads]):
            self._event.wait(0.5)
        self._when_done()

    def _when_done(self):
        if self.output:
            with open(self.output, 'w') as f:
                if self.as_json:
                    j = json.dumps(self._output)
                    f.write(j)
                    sys.stdout.write(j)
                else:
                    f.write(self._output)


def valid_args(args):
    """
    returns a reason if args are not valid,
    returns none if there is no reason that the arg is not valid
    """
    required = ['domain', 'wordlist']

    for req in required:
        if args[req] == None:
            return 'missing required argument %s' %req

def main(args):

    if not os.path.exists(args.config):
        raise Exception('config file %s does not found' %args.config)

    with open(args.config, 'r') as fd:
        config = json.load(fd)

    defaults = [
        'threads', 'output', 'domain', 
        'wordlist', 'time', 'json'
    ]

    for field in defaults:
        config.setdefault(field, getattr(args, field))

    if reason:=valid_args(config):
        raise Exception(reason)

    if not os.path.exists(config['wordlist']):
        raise Exception('wordlist %s not found' %config['wordlist'])
    
    with open(config['wordlist'], 'r') as fd:
        wrds = fd.readlines()
    
    wrds_sum = len(wrds)
    wrds_per_thread = math.ceil(wrds_sum / config['threads'])
    
    manager = WorkerManager(
        wrds=wrds,
        wrds_sum=wrds_sum,
        wrds_per_thread=wrds_per_thread,
        domain=config['domain'],
        workers=config['threads'],
        json=config['json'],
        output=config['output'],
        time=config['time']
    )
    manager.create_workers()
    manager.work()


if __name__ == '__main__':
    parse = argparse.ArgumentParser(sys.argv[0])
    parse.add_argument('-c', '--config', 
        help='config file path', 
        type=str,
        default='conf.json'
    )
    parse.add_argument('-T', '--time',
        help='aggressiveness, like nmap -T',
        choices=list(range(1, 6)), 
        type=int, 
        default=3
    )
    parse.add_argument('-t', '--threads',
        help='how many threads use',
        type=int,
        default=10
    )
    parse.add_argument('-w', '--wordlist', 
        help='a word list to loop over',
        type=str
    )
    parse.add_argument('-d', '--domain', 
        help='root domain',
        type=str
    )
    parse.add_argument('-o', '--output',
        help='output report file',
        type=str
    )
    parse.add_argument('-j', '--json',
        help='output to stdout and output file (if there is any) in json format only',
        type=bool,
        nargs='?',
        const=True,
        default=False
    )
    main(parse.parse_args(sys.argv[1:]))
