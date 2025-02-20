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

    logDir = plib.Path(
        "/".join(
                str(logPath).split("/")[:-1]
            )
    )

    try:
        logDir.mkdir(parents=True, exist_ok=False)
        fileMode = "w"
    except FileExistsError:
        if not logPath.exists():
            fileMode = "w"

    with open(logPath, fileMode) as f:
        f.write(f"{string}")
        f.write(f"{end}")
    
    if verbose:
        print(f"{string}", end=end) 
    
    return None

#------------------------------------------------------------------------------

def check_lastsync_time(
        syncTimesDir:plib.Path,
        idName:str,
        logPath:plib.Path,
        verbose=False,
    )->dtm.timedelta:

    currentTimePath = syncTimesDir / f"last_synctime_{idName}.yaml"

    try:
        syncTimesDir.mkdir(exist_ok=False)
    except FileExistsError:
        log(string=f"{syncTimesDir} already exists.", 
            logPath=logPath,
            verbose=verbose)
        
    if not currentTimePath.exists():
        with open(currentTimePath, "w") as f:
            now = dtm.datetime.now()
            f.write(f"year: {now.year}\n")
            f.write(f"month: {now.month}\n")
            f.write(f"day: {now.day}\n")
            f.write(f"hour: {now.hour}\n")
            f.write(f"minute: {now.minute}\n")
            f.write(f"second: {now.second}\n")

        return now - now

    else:
        with open(currentTimePath, "r") as f:
            lastSyncTime = yml.load(f, Loader=yml.FullLoader)
        
        with open(currentTimePath, "w") as f:
            now = dtm.datetime.now()
            f.write(f"year: {now.year}\n")
            f.write(f"month: {now.month}\n")
            f.write(f"day: {now.day}\n")
            f.write(f"hour: {now.hour}\n")
            f.write(f"minute: {now.minute}\n")
            f.write(f"second: {now.second}\n")

        return dtm.datetime.now() - dtm.datetime(
            year=lastSyncTime["year"],
            month=lastSyncTime["month"],
            day=lastSyncTime["day"],
            hour=lastSyncTime["hour"],
            minute=lastSyncTime["minute"],
            second=lastSyncTime["second"],
        )
        
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

def run_backup(
        configs:dict, 
        logPath:plib.Path, 
        verbose=False
    )->None:

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

def main(
        configsPath:plib.Path, 
        logPath:plib.Path, 
        timeStampFolder:plib.Path, 
        verbose=False
    )->None:
    
    configs = read_configs(configsPath=configsPath, 
                           logPath=logPath, 
                           verbose=verbose)
    
    current_config:dict = {}
    for key in configs.keys():
        if configs[key]["every"]["set"]:
            every=dtm.timedelta(
                days=configs[key]["every"]["days"],
                hours=configs[key]["every"]["hours"],
                minutes=configs[key]["every"]["minutes"],
                seconds=configs[key]["every"]["seconds"],
            )


            log(string=f"synchronization delta: {every}", logPath=logPath, verbose=verbose)
            deltaTimeNow = check_lastsync_time(
                syncTimesDir=timeStampFolder,
                idName=key,
                logPath=logPath,
                verbose=True,
            )

            if deltaTimeNow > every:
                current_config = {key : configs[key]}
                run_backup(configs=current_config, logPath=logPath, verbose=verbose)
    return 

#------------------------------------------------------------------------------

if __name__ == "__main__":

    configsPath:plib.Path = plib.Path('~').expanduser() / "configs" / "pyrsync_configs.yaml"
    logPath:plib.Path = plib.Path('~').expanduser() / ".data" / "logs" / "pyrsync" /"pyrsync.log"
    verbose:bool = False

    for argId, arg in enumerate(sys.argv[:]):
        if arg == "--help" or arg == "-h":
            manPath = plib.Path(
                    "/".join(
                    str(plib.Path(__file__).parent.resolve()).split("/")[:]
                )
            ) / "man.txt"
            try:
                with open(manPath, "r") as f:
                    lines = f.readlines()

                for line in lines:
                    print(line, end="")
            
                print()

            except FileNotFoundError:
                print("man file does not exist")
            exit(0) 

        if arg == "--conf" or arg == "-c":
            configsPath = plib.Path(sys.argv[argId + 1])
        if arg == "--log" or arg == "-l":
            logPath = plib.Path(sys.argv[argId + 1])
        if arg == "--verbose" or arg == "-v":
            verbose = True
        

    for argId, arg in enumerate(sys.argv[:]):
        if arg == "--viewlog":
            
            try:
                with open(logPath, "r") as f:
                    lines = f.readlines()

                for line in lines:
                    print(line, end="")
            
                print()

            except FileNotFoundError:
                print("log file does not exist")
            exit(0) 


    timeStampFolder = plib.Path("/".join(str(logPath).split("/")[:-1])) / "time_stamps"

    now = dtm.datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    
    log(
        string=f"Starting: {now}", 
        logPath=logPath, 
        verbose=verbose
    )
    
    main(
        configsPath=configsPath, 
        logPath=logPath, 
        timeStampFolder=timeStampFolder, 
        verbose=verbose
    )

    now = dtm.datetime.now().strftime("[%d-%m-%Y %H:%M:%S]")
    log(string=f"Done: {now}", logPath=logPath, verbose=verbose)
    log(string=f"{'-'*80}", logPath=logPath, verbose=verbose)

#------------------------------------------------------------------------------
