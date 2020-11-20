#! /usr/bin/env bash

# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

if [ "$#" -lt 2 ]; then
    echo >&2 "usage: $0 <dolphin-emu> <file.dff:out-dir ...>"
    exit 1
fi

BASE=$(dirname $0)
SCRIPTNAME=$(basename $0)
TIMEOUT=2m

if [ -z "$FIFOCI_NO_TIMEOUT" ]; then
    TIMEOUT_CMD="timeout -s 9 $TIMEOUT"
else
    TIMEOUT_CMD=""
fi

LIBSEGFAULT=""
for f in /lib/x86_64-linux-gnu/libSegFault.so /lib/libSegFault.so /lib64/libSegFault.so; do
  if [ -e $f ]; then
    LIBSEGFAULT=$f
    break
  fi
done
echo "Using libSegFault: $LIBSEGFAULT"

show_logs() {
    sed "s/^/$1>>> /"
}

BACKEND=$1; shift
DRIVER=$1; shift
DOLPHIN=$1; shift

echo "FIFOCI Worker starting for $DOLPHIN"

while [ "$#" -ne 0 ]; do
    DFF=$(echo "$1" | cut -d : -f 1)
    OUT=$(echo "$1" | cut -d : -f 2)

    echo "Processing FIFO log $DFF (output to $OUT)"

    # Use a temporary directory to store the Dolphin profile.
    export HOME=$(mktemp -d /tmp/dolphin.XXXXXXXXXX)
    echo "Using $HOME as our temporary home"
    mkdir -p $HOME/.dolphin-emu
    cp -r $BASE/Config-$BACKEND $HOME/.dolphin-emu/Config

    DUMPDIR=$HOME/.dolphin-emu/Dump/Frames
    mkdir -p $DUMPDIR

    echo "Starting DolphinNoGui with a $TIMEOUT timeout"

    EGL_PLATFORM=surfaceless \
    LD_PRELOAD=$LIBSEGFAULT SEGFAULT_SIGNALS="abrt segv" \
      $TIMEOUT_CMD $DOLPHIN -p headless -e $DFF &> >(show_logs Dolphin)
    if [ "$?" -ne 0 ]; then
        echo "FIFO log playback failed for $DFF"
        touch $OUT/failure
    else
        echo "FIFO playback done, extracting frames to $OUT"

        AVIFILE=$(echo $DUMPDIR/*.avi)
        if [ -f "$AVIFILE" ]; then
            ffmpeg -i "$AVIFILE" -f image2 $OUT/frame-%3d.png \
                &> >(show_logs ffmpeg)
        else
            # Assume SW renderer style of .png frame dumping.
            i=0
            for f in $(ls -rt $DUMPDIR/*.png); do
                convert -alpha deactivate $f `printf $OUT/frame-%03d.png $i`
                i=$((i + 1))
            done
        fi
    fi
    chmod g+r -R $OUT

    rm -rf $HOME
    shift
done

echo "Processing done."
