#!/usr/bin/env python3

import subprocess
import click
import logging
import sys
import shlex
from common import *
from hls_internal import *
from hls_internal.HLSDownloader import *
from hls_internal.OutputBuilder import *
import tracemalloc
import tqdm
import random

def readList(fname: str) -> list:
    if not os.path.isfile(fname):
        raise "%s not a file" % fname
    with open(fname, "r") as f:
        lines = []
        for line in f:
            s = line.strip()
            if s and s[0] != "#":
                lines.append(s)
        return lines

@click.group()
def cli():
    pass

@cli.command()
@click.argument('job')
@click.option('--format', '-f', default=OutputFormat.Json, type=click.Choice([OutputFormat.Json, OutputFormat.SqLite, OutputFormat.PrettyPrint], case_sensitive=False))
@click.option('--filter', default=OutputFormat.Json, type=click.Choice([ResultFilter.FilterAvailable, ResultFilter.FilterOnOff, ResultFilter.FilterAsIs], case_sensitive=False), help="what should be printed")
@click.option('--target', '-O', default=ReservedTargets.stdout, help="output target. filename or stdout[default]")
@click.option('--verbose', '-v', is_flag=True, default=False, help="print verbose logs")
@click.option('--jobs', '-j',  default=8, help="parallel jobs")
@click.option('--nofollow', is_flag=True, default=False, help="disable recursive playlist scan")
def scan(job, format, filter, target, verbose, jobs, nofollow):
    if jobs < 1:
        print("invalid jobs count %d. set 1" % jobs)
    mprint('scan. job: %s -> %s[%s]' % (job, target, format))
    Globals.verbose = verbose
    l = readList(job)
    if not l:
        eprint("nothing to do in job file")
        return
    mprint('scan. %d records in job' % len(l))
    results = []
    printer = ResultPrinter(format, target)
    pool = []
    poolSize = jobs
    random.shuffle(l)
    nf = ""
    if nofollow:
        nf = " --nofollow "
    for u in tqdm.tqdm(l, desc='Total'):
        if "@" in u:
            mprint("hls cannot process urls with @. ignore %s " % u)
            continue
        if not u.isascii():
            mprint("invalid chars in %s" % u)
            continue
        try:
            if len(pool) < poolSize:
                cmd = "hls stat --flow --single --delay %s %s" % (nf, u)
                args = shlex.split(cmd)
                p = subprocess.Popen(args, stdout=subprocess.PIPE)
                pool.append((p, u))
                continue
            p, wait_u = pool[0]
            pool.pop(0)
            #p.wait()
            mprint("wait task for %s" % wait_u)
            sys.stdout.flush()
            p_out = p.communicate()
            sys.stdout.flush()
            out = ""
            if p_out:
                if p_out[0]:
                    out = p_out[0].strip()
                if p_out[1]:
                    mprint("subprocess stderr %s" % str(p_out[1]))
            else:
                eprint("no output for %s " % u)
                continue
            obj = None
            if not out:
                eprint("empty out for %s" % u)
                continue
            try:
                obj = json.loads(out)
            except Exception as e:
                eprint("json load error %s out %s" % (str(e), str(out)))
                return
            if not obj or not obj['stat']:
                eprint("invalid subprocess output for %s" % u)
                continue
            for stat in obj['stat']:
                stat['available'] = obj['ok']
                results.append(stat)


        except subprocess.CalledProcessError as e:
            eprint("subprocess error in \ncmd: %s \nout: {%s}\nerr:{%s}" % (cmd, e.output, e.stderr))
            return


    pkg = ResultPkg(results)
    filter = filter.strip().lower()
    mprint("use filter: %s" % filter)
    if filter and filter != ResultFilter.FilterAsIs:
        pkg = ResultFilter.statfilter(filter, pkg)
    printer.print(pkg)


@cli.command()
def download():
    click.echo('Dropped the database')

if __name__ == "__main__":
    try:
        logging.basicConfig(filename='hls_batch.%d.log' % (mstime()), encoding='utf-8', level=logging.DEBUG)
    except ValueError:
        logging.basicConfig(filename='hls_batch.%d.log' % (mstime()), level=logging.DEBUG)
    tracemalloc.start()
    cli()
    logging.shutdown()