# hls_utils
usage: hls [-h] [-o OUT] [-1] [-v] [--config CONFIG] [--flow] [--nofollow] [--delay] [--savemeta] [-z] cmd url
```
HLS tool

positional arguments:
  cmd                what do we do. variants: [ 'download', 'scan', 'stat', 'available', 'media']
  url                stream url

optional arguments:
  -h, --help         show this help message and exit
  -o OUT, --out OUT  download folder
  -1, --single       single run. test and exit
  -v, --verbose      full console output
  --config CONFIG    config file
  --flow             flow mode. json output only
  --nofollow         process only top playlist
  --delay            random sleep before start
  --savemeta         save metainfo (playlists, text files, etc...)
  -z, --zip          compress meta files
  ```
  
## commands:
 - **download** - download hls content from url. use key --savemeta to dump playlists too
 - **scan** - print download status of playlist from url. ok ornot ok (with reason)
 - **stat** - providex extended information about playlist like bandwidth, duration, etc. works recursively. prints results to *'results.%d.%d.txt'* files and to stdout with **-v** 
 - **available** - loads list of hls sources and test entries for availability
 - **media** - extracts media playlists from master url

## examples:
see notebooks in **lists** folder

---

## howto:
 - dump hls? ```hls download --savemeta -v url```