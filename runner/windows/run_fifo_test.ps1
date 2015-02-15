# This file is part of the FifoCI project.
# Copyright (c) 2014 Pierre Bourdon <delroth@dolphin-emu.org>
# Licensing information: see $REPO_ROOT/LICENSE

if ($args.length -lt 3) {
  write-error "usage: rft.ps1 <backend> <driver> <dolphin> <spec...>"
  throw "Not enough arguments."
}

$backend = $args[0]
$driver = $args[1]
$dolphin = $args[2]

if (-not (test-path $dolphin)) {
  throw "$dolphin does not exist. No binary, no test."
}

$srcconfigdir = join-path $PSScriptRoot -child ("Config-$backend-$driver")
if (-not (test-path $srcconfigdir)) {
  throw "$srcconfigdir does not exist. No configuration for this backend!"
}

$dolphindir = (get-item $dolphin).Directory.Name
$userdir = join-path $dolphindir -child User
if (test-path $userdir) {
  throw "$userdir already exists! Not a clean run?"
}
$portablefile = join-path $dolphindir -child portable.txt
echo $null >> $portablefile

foreach ($spec in $args[3..$args.length]) {
  $spec = $spec.split(":")
  if ($spec.length -ne 2) {
    throw ("invalid spec: $spec")
  }

  $dff = $spec[0]
  $out = $spec[1]
  write-host "Running $dff with results to output directory $out"

  new-item -itemtype Directory -path $userdir
  robocopy $srcconfigdir (join-path $userdir -child "Config")

  $proc = start-process -passthru "$dolphin" "/b /e $dff"
  $success = $TRUE
  if (-not $proc.WaitForExit(60000)) {
    $proc.Kill()
    write-host "$dff playback timed out after 60s"
    $success = $FALSE
  }
  if ($proc.ExitCode -ne 0) {
    write-host "$dff playback failed with exit code $($proc.ExitCode)"
    $success = $FALSE
  }

  $avifile = "$userdir/Dump/Frames/framedump0.avi"
  if (-not (test-path $avifile)) {
    write-host "$dff playback did not generate a frame dump"
    $success = $FALSE
  }

  if ($success) {
    start-process -wait "ffmpeg" "-i $avifile -f image2 $out/frame-%3d.png"
  } else {
    echo $null >> (join-path $out -child failure)
  }

  remove-item -recurse -force $userdir
}
