#! /bin/bash

# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

if [ "$#" -lt 2 ]; then
    echo >&2 "usage: $0 <dolphin-emu> <file.dff:out-dir ...>"
    exit 1
fi

BASE=$(dirname $0)
TIMEOUT=2m

if [ -z "$FIFOCI_NO_TIMEOUT" ]; then
    TIMEOUT_CMD="timeout -s 9 $TIMEOUT"
else
    TIMEOUT_CMD=""
fi

show_logs() {
    sed "s/^/$1>>> /"
}

BACKEND=$1; shift
DRIVER=$1; shift
DOLPHIN=$1; shift

echo "FIFOCI Worker starting for $DOLPHIN"

# Start a dummy X server on :1.
# TODO(delroth): Find the next usable display.
export DISPLAYNUM=1
export DISPLAY=:$DISPLAYNUM
echo "Starting a headless Xorg server on $DISPLAY"
if [ -f "$HOME/fifoci-xorg.conf" ]; then
    XORG_CFG="$HOME/fifoci-xorg.conf"
else
    XORG_CFG="$BASE/xorg.conf"
fi
sudo Xorg -noreset +extension GLX +extension RANDR +extension RENDER \
    -config $XORG_CFG $DISPLAY &> >(show_logs Xorg) &
XORG_PID=$!

while ! [ -e "/tmp/.X11-unix/X$DISPLAYNUM" ]; do
    echo "Waiting for the X11 server to be ready..."
    sleep 0.1
done

echo 'Ready to process FIFO logs \o/'

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

    $TIMEOUT_CMD $DOLPHIN -e $DFF &> >(show_logs Dolphin)
    if [ "$?" -ne 0 ]; then
        echo "FIFO log playback failed for $DFF"
        touch $OUT/failure
    else
        echo "FIFO playback done, extracting frames to $OUT"

        AVIFILE=$DUMPDIR/framedump0.avi
        if [ -f "$AVIFILE" ]; then
            ffmpeg -i $AVIFILE -f image2 $OUT/frame-%3d.png \
                &> >(show_logs ffmpeg)
        else
            # Assume SW renderer style of .png frame dumping.
            i=0
            for f in $(ls -rt $DUMPDIR/*.png); do
                mv -v $f `printf $OUT/frame-%03d.png $i`
                i=$((i + 1))
            done
        fi
    fi
    chmod g+r -R $OUT

    rm -rf $HOME
    shift
done

echo "Processing done, cleaning up"

# Cleanup: kill Xorg, rm the temporary directory.
sudo kill $XORG_PID
wait $XORG_PID
