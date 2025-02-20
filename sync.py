import sys
import yaml as yml
import pathlib as plib
import datetime as dtm
import subprocess

#------------------------------------------------------------------------------
def log(
        string:str, 
        logPath:plib.Path, 
        verbose:bool = False,
        end:str="\n",
    )->None:

    fileMode = "a"
    if not logPath.exists():
        fileMode = "w"

    with open(logPath, fileMode) as f:
        f.write(f"{string}")
        f.write(f"{end}")
    
    if verbose:
        print(f"{string}", end=end) 
    
    return None

#------------------------------------------------------------------------------

def read_configs(
        configsPath: plib.Path, 
        logPath:plib.Path,
        verbose:bool=False
    )-> dict:
    configs:dict = {}

    log(string=f"Reading configs from {configsPath}", logPath=logPath, 
        verbose=verbose,end="\t")
    
    with open(configsPath, "r") as f:
        try:
            configs.update(yml.load(f, Loader=yml.FullLoader))
        except Exception as E:
            log(string=f"Error occured while reading {configsPath}", 
                logPath=logPath, verbose=True)
            for arg in E.args:
                log(string=str(arg), logPath=logPath, verbose=True)

    log(string="Done!", logPath=logPath, verbose=verbose, end="\n")
    return configs

#------------------------------------------------------------------------------

def rsync(
        source:plib.Path, 
        destination: plib.Path, options:list, 
        logPath:plib.Path,
        verbose=False,
    ) ->None:

    command = ["rsync"]
    for opt in options:
        command.append(opt)

    command.append(str(source))
    command.append(str(destination))

    log(string=' '.join(command), logPath=logPath, verbose=verbose)

    result = subprocess.run(
        command, 
        check=True, 
        text=True, 
        capture_output=True,
    )

    log(string=result.stdout, logPath=logPath, verbose=verbose)

#------------------------------------------------------------------------------

def run_backup(configs:dict, logPath:plib.Path, verbose=False)->None:
    assert isinstance(configs, dict), f"Variable 'configs' should be a dict"
    idNames:list = list(configs.keys())

    offsetStr:str = "\t"
    level:int = 0
    for idName in idNames:
        log(f"{offsetStr*level}{idName}", logPath=logPath, verbose=verbose)
        level += 1
        for key in ["src", "dst"]:
            assert key in list(configs[idName].keys()), f"key {key} is missing in configs of {idName}"
            log(f"{offsetStr*level}{key}: {configs[idName][key]}", logPath=logPath)
        
        src = plib.Path(configs[idName]['src'])
        dst = plib.Path(configs[idName]['dst'])

        assert src.exists(), f"{src} does not exist"
        if not dst.exists(): dst.mkdir(parents=True, exist_ok=False)

        rsyncOpts = ["-avz"]
        
        rsync(source=src, destination=dst, 
              options=rsyncOpts, logPath=logPath,
              verbose=verbose)

        level -= 1

    return

#------------------------------------------------------------------------------

def main(configsPath:plib.Path, logPath:plib.Path, verbose=False)->None:
    configs = read_configs(configsPath=configsPath, 
                           logPath=logPath, 
                           verbose=verbose)
    run_backup(configs=configs, logPath=logPath, verbose=verbose)
    return 

#------------------------------------------------------------------------------

if __name__ == "__main__":

    configsPath:plib.Path = plib.Path('~').expanduser() / "configs" / "sync_configs.yaml"
    logPath:plib.Path = plib.Path('~').expanduser() / "logs" / "sync.log"
    verbose:bool = False

    for argId, arg in enumerate(sys.argv[:]):
        if arg == "--help" or arg == "-h":
            usage = """
            Usage:
                pyrsync --conf path/to/configfile --log path/to/logfile
                            OR
                pyrsync -c path/to/configfile -l path/to/logfile
                    Read config file from path/to/configfile and log to 
                    path/to/logfile
                pyrsync --verbose [options] OR pyrsync -v [options]
                    Enable verbose with options
                pyrsync
                    Read configs from the default path : ~/configs/sync_configs.yaml
                    and
                    logs to default logfile: ~/logs/sync.log
            """
            print(usage)
            exit(0) 
        if arg == "--conf" or arg == "-c":
            configsPath = plib.Path(sys.argv[argId + 1])
        if arg == "--log" or arg == "-l":
            logPath = plib.Path(sys.argv[argId + 1])
        if arg == "--verbose" or arg == "-v":
            verbose = True

    now = dtm.datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    
    log(string=f"Starting: {now}", logPath=logPath, verbose=verbose)
    main(configsPath=configsPath, logPath=logPath, verbose=verbose)
    now = dtm.datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    log(string=f"Done: {now}", logPath=logPath, verbose=verbose)
    log(string=f"{'-'*80}", logPath=logPath, verbose=verbose)

#------------------------------------------------------------------------------
