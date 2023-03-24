import sys
from io import StringIO
from pathlib import Path
from shutil import copyfile

from streamlit.web import cli

def runner(args=None):
    capout = StringIO()
    caperr = StringIO()
    sys.stdout = capout
    sys.stderr = caperr
    if args is not None:
        sys.argv = args
    try:
        import pyi_splash
        pyi_splash.close()
    except:
        pass
    sys.exit(cli.main())

if __name__ == "__main__":
    cfgdir = Path.home() / ".streamlit"
    cfgdir.mkdir(exist_ok=True)
    credfile = cfgdir / "credentials.toml"
    if not credfile.exists():
        copyfile("./credentials.toml", credfile)
    args = [
        "--browser.gatherUsageStats=false",
        "--server.fileWatcherType='none'",
        "--server.maxUploadSize=1000",
        "--runner.fastReruns=true",
        "--runner.magicEnabled=false",
        "--logger.level=info",
        "--global.developmentMode=false",
        "--global.dataFrameSerialization=arrow",
        "--theme.base=dark"
    ]
    callstr = "streamlit run ./app/Home.py"
    runner(callstr.split() + args)