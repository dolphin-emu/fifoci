#! /bin/bash

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
DOLPHIN=$1; shift

echo "FIFOCI Worker starting for $DOLPHIN"

# Start a dummy X server on :1.
# TODO(delroth): Find the next usable display.
export DISPLAYNUM=1
export DISPLAY=:$DISPLAYNUM
echo "Starting a headless Xorg server on $DISPLAY"
sudo Xorg -noreset +extension GLX +extension RANDR +extension RENDER \
    -config $BASE/xorg.conf $DISPLAY &> >(show_logs Xorg) &
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

    echo "Starting DolphinNoGui with a $TIMEOUT timeout"

    $TIMEOUT_CMD $DOLPHIN -e $DFF &> >(show_logs Dolphin)
    if [ "$?" -ne 0 ]; then
        echo "FIFO log playback failed for $DFF"
        touch $OUT/failure
    else
        echo "FIFO playback done, extracting frames with ffmpeg to $OUT"

        # TODO(delroth): This only works for OpenGL/D3D, check how frame
        # dumping works on the SW renderer.
        ffmpeg -i $HOME/.dolphin-emu/Dump/Frames/framedump0.avi -f image2 \
               $OUT/frame-%3d.png &> >(show_logs ffmpeg)
    fi
    chmod g+r -R $OUT

    rm -rf $HOME
    shift
done

echo "Processing done, cleaning up"

# Cleanup: kill Xorg, rm the temporary directory.
sudo kill $XORG_PID
wait $XORG_PID
