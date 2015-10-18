# trawler-python-region-scan
Simple WA scanner for a region

## Setup

```bash
$ git clone trawler-python-region-scan
$ cd trawler-python-region-scan
$ git submodule update --init --recursive
$ cd parser/client
$ protoc --proto_path=./protocol/ --python_out=. ./protocol/trawler.proto
$ cd ../..
```

Also install the requirements for [the parser](protoc --proto_path=./protocol/ --python_out=. ./protocol/trawler.proto; cd ../..
) and [the daemon](https://github.com/Eluvatar/trawler-daemon-c) (and set up the daemon).

Example usage:

```bash
$ ./wa_scanner -r your_region -u your_email@some`crazy.domain.com -o top_25.json
$ python -m json.tool < top_25.json
```
