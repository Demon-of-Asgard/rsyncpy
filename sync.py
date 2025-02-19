import sys
import yaml as yml
import pathlib as plib
import datetime as dtm
import subprocess

#------------------------------------------------------------------------------
def log(
        string:str, 
        logPath:plib.Path, 
        end:str="\n"
    )->None:

    fileMode = "a"
    if not logPath.exists():
        fileMode = "w"

    with open(logPath, fileMode) as f:
        f.write(f"{string}")
        f.write(f"{end}")
    
    return None

#------------------------------------------------------------------------------

def read_configs(
        configsPath: plib.Path, 
        logPath:plib.Path
    )-> dict:
    configs:dict = {}
    log(f"Reading congigs from {configsPath}", logPath=logPath, end="\t")
    with open(configsPath, "r") as f:
        configs.update(yml.load(f, Loader=yml.FullLoader))
    log("Done!", logPath=logPath, end="\n")
    return configs

#------------------------------------------------------------------------------

def rsync(
        source:plib.Path, 
        destination: plib.Path, options:list, 
        logPath:plib.Path
    ) ->None:

    command = ["rsync"]
    for opt in options:
        command.append(opt)

    command.append(str(source))
    command.append(str(destination))

    log(' '.join(command), logPath=logPath)

    result = subprocess.run(
        command, 
        check=True, 
        text=True, 
        capture_output=True,
    )

    log(result.stdout, logPath=logPath)

#------------------------------------------------------------------------------

def run_backup(configs:dict, logPath:plib.Path)->None:
    assert isinstance(configs, dict), f"Variable 'configs' should be a dict"
    idNames:list = list(configs.keys())

    offsetStr:str = "\t"
    level:int = 0
    for idName in idNames:
        log(f"{offsetStr*level}{idName}", logPath=logPath)
        level += 1
        for key in ["src", "dst"]:
            assert key in list(configs[idName].keys()), f"key {key} is missing in configs of {idName}"
            log(f"{offsetStr*level}{key}: {configs[idName][key]}", logPath=logPath)
        
        src = plib.Path(configs[idName]['src'])
        dst = plib.Path(configs[idName]['dst'])

        assert src.exists(), log("does not exist", logPath=logPath)
        if not dst.exists(): dst.mkdir(parents=True, exist_ok=False)

        rsyncOpts = ["-avz"]
        
        rsync(source=src, destination=dst, options=rsyncOpts, logPath=logPath)

        level -= 1
    return

#------------------------------------------------------------------------------

def main(configsPath:plib.Path, logPath:plib.Path):
    configs = read_configs(configsPath=configsPath, logPath=logPath)
    run_backup(configs=configs, logPath=logPath)

#------------------------------------------------------------------------------

if __name__ == "__main__":

    configsPath = plib.Path('~').expanduser() / "configs" / "sync_configs.yaml"
    logPath = plib.Path('~').expanduser() / "logs" / "sync.log"
    
    for argId, arg in enumerate(sys.argv[:]):
        if arg == "--help" or arg == "-h":
            usage = """
                    Usage:
                        rsync --conf path/to/configfile --log path/to/logfile
                            Read config file from path/to/configfile and log to 
                            path/to/logfile
                        rsync 
                            Read configs from the default path : ~/configs/sync_configs.yaml
                            and
                            logs to default logfile: ~/logs/sync.log
                    """
            print(usage)
            exit(0) 
        if arg == "--conf":
            configsPath = plib.Path(sys.argv[argId + 1])
        if arg == "--log":
            logPath = plib.Path(sys.argv[argId + 1])
    now = dtm.datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    
    log(f"Starting: {now}", logPath=logPath)
    main(configsPath=configsPath, logPath=logPath)
    now = dtm.datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    log(f"Done: {now}", logPath=logPath)
    log(f"{'-'*80}", logPath=logPath)

#------------------------------------------------------------------------------
