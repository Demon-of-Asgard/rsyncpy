# rsyncpy
Python script for using rsync to backup files and folders


##                        [Usage]

pyrsync [option(s)]

If no options specified, script will read configs from the 
default path at ~/configs/sync_configs.yaml and logs to default 
logfile at ~/.data/logs/pyrsync/pyrsync.log

[options]

    To read config file from path/to/configfile and log to
        --conf path/to/configfile 
            OR
        -c path/to/configfile

    To write log to  path/to/logfile
        --log path/to/logfile
            OR
        -l path/to/logfile


    Enable verbose with options
    --verbose 
        OR 
    -v 

    Display logs from default logfile if exist
        --viewlog

    Display logs from custom logfile if exist
        --viewlog --log path/to/logfile

