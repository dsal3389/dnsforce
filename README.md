# dnsforce
a DNS bruteforce, simple and fast with json output

## legal
any use of this script on unauthorized networks make the user the responsible and not the developer

## config file / flags

| field    | type    | description                                                                     |
|----------|---------|---------------------------------------------------------------------------------|
| output   | string  | output to the given filename in a text format (for json format use the -j flag) |
| threads  | int     | number of threads the script should use                                         |
| time     | int     | like NMAP aggressiveness, can be change, change in variable named: aggr_options |
| wordlist | string  | word list to use for bruteforce                                                 |
| json     | boolean | if output in json format                                                        |
| domain   | string  | the root domain to bruteforce                                                   |

## examples
you can use this script in 2 simple ways,
    1. is a config file with all flags in there
    2. you can pass the flags to the program

```
foo@foo:~$ python3 main.py -T 3 --json --domain foo.com
```

or you can pass the config file and the script will retrive all the information from there
```
foo@foo~$ python3 main.py --config foo.conf
```

## example config file 
```
{
    "threads": 10,
    "domain": "domain.com",
    "output": "results.txt",
    "wordlist": "wordlist.txt",
    "time": 3,
    "json": false
}
```