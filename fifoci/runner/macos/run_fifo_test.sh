#!/bin/bash

# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Copyright (c) 2021 OatmealDome <julian@oatmealdome.me>
# Licensing information: see $REPO_ROOT/LICENSE

if [ "$#" -lt 2 ]; then
    echo >&2 "usage: $0 <dolphin-emu> <file.dff:out-dir ...>"
    exit 1
fi

BASE=$(dirname $0)
SCRIPTNAME=$(basename $0)
TIMEOUT=2m

if [ -z "$FIFOCI_NO_TIMEOUT" ]; then
    TIMEOUT_CMD="gtimeout -s 9 $TIMEOUT"
else
    TIMEOUT_CMD=""
fi

show_logs() {
    sed "s/^/$1>>> /"
}

BACKEND=$1; shift
DRIVER=$1; shift
BINARIES=$1; shift # path to Binaries directory

echo "FIFOCI Worker starting for $DOLPHIN"

while [ "$#" -ne 0 ]; do
    DFF=$(echo "$1" | cut -d : -f 1)
    OUT=$(echo "$1" | cut -d : -f 2)

    echo "Processing FIFO log $DFF (output to $OUT)"

    # Use a temporary directory to store the User directory.
    export DOLPHIN_EMU_USERPATH=$(mktemp -d)/
    echo "Using $DOLPHIN_EMU_USERPATH as our User directory"
    cp -r $BASE/Config-$BACKEND $DOLPHIN_EMU_USERPATH/Config

    # Set LIBVULKAN_PATH to the MoltenVK dylib within the DolphinQt bundle.
    export LIBVULKAN_PATH=$BINARIES/Dolphin.app/Contents/Frameworks/libMoltenVK.dylib

    # Enable all the Metal validation
    export MTL_DEBUG_LAYER=1
    # export MTL_SHADER_VALIDATION=1

    DUMPDIR=$DOLPHIN_EMU_USERPATH/Dump/Frames
    mkdir -p $DUMPDIR

    echo "Starting DolphinNoGui with a $TIMEOUT timeout"

    $TIMEOUT_CMD $BINARIES/dolphin-emu-nogui -p headless -e $DFF &> >(show_logs Dolphin)
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
            # Assume PNG frame dumping.
            i=1
            for f in $(ls -rt $DUMPDIR/*.png); do
                mv -v $f `printf $OUT/frame-%03d.png $i`
                i=$((i + 1))
            done
        fi
    fi
    chmod -R g+r $OUT

    rm -rf $DOLPHIN_EMU_USERPATH
    shift
done

echo "Processing done."
