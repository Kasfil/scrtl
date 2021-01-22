#!/bin/python3

import argparse
import datetime
import os
import pathlib
import subprocess
import time

from datetime import date

# default save path
defaultPath = pathlib.Path.home().joinpath('Videos').joinpath('scrtl')
# list of unsupported tools
tools = ['flameshot', 'maim', 'grim', 'imlib2', 'shotgun']

# set command and args to capture your screen
def defineCommand():
  tool = args.tool
  if tool == 'flameshot':
    # Because flameshot doesn't support inline file naming
    # then set in config first to avoid indexing mistake
    subprocess.run([tool, 'config', '-f', '%Y%m%d%H%M%S'], capture_output=True)
    return [tool, 'full', '-p']
  else:
    return [tool]

# capture function
def startCapture():
  realpath = os.path.abspath(args.path)
  # move working dir to save path
  os.chdir(realpath)
  # get capture command
  initCmd = defineCommand()
  # the number count to start
  startAt = args.start
  # start capture after 2 second to get ready
  time.sleep(2)
  while True:
    # if tool not flameshot insert leading zero count number
    # based on args.start like 00XX.png
    capture_count = str(f'{startAt:04d}') + '.png'
    # capture screen
    if args.tool != 'flameshot':
      subprocess.run(initCmd + [capture_count], capture_output=False)
    else:
      subprocess.run(initCmd + [realpath], capture_output=False)
    # using sleep to delay next capture
    print('%s captures collected' % startAt)
    time.sleep(args.delay)
    startAt += 1

# Render video
def render2Video():
  print('\n\nProcessing image into video.....')
  filename = 'scrtl_' + datetime.datetime.now().strftime('%Y%m%d%H%M') + '.mp4'
  subprocess.run([
    'ffmpeg',
    # set framerate
    '-framerate', str(args.fps),
    # image to process
    '-f', 'image2',
    '-pattern_type', 'glob',
    '-i', '*.png',
    # encode to mp4
    '-an',
    '-vcodec', 'libx264',
    '-b:v', '4M',
    '-b:a', '320k',
    '-acodec', 'copy',
    # filename output
    filename
  ], capture_output=True)
  print('Generated video saved in {}/{}'.format(args.path, filename))

parser = argparse.ArgumentParser(
  prog="scrtl",
  description="Create screen timelapse"
)
# FPS argument
parser.add_argument(
  '-f', '--fps',
  default=24,
  metavar='NUM',
  type=int,
  help="FPS for generated video"
)
# Delay each capture delay argument
parser.add_argument(
  '-d', '--delay',
  default=5,
  metavar='NUM',
  type=int,
  help="Delay between each capture"
)
# Path to save image and generated video
parser.add_argument(
  '-p', '--path',
  default=defaultPath,
  type=pathlib.Path,
  help="Path to save captured image and generated video"
)
# number where the count to start
parser.add_argument(
  '-s', '--start',
  default=1,
  metavar='INT',
  type=int,
  help='Number where the count to start Have no effect in flameshot'
)
# tools selected to capture screen
parser.add_argument(
  'tool',
  metavar='tool',
  choices=tools,
  help='App to capture your screen'
)

# Parse arguments
args = parser.parse_args()

# Check if save path is available
realpath = os.path.abspath(args.path)
if not pathlib.Path(realpath).is_dir():
  try:
    os.makedirs(realpath)
  except OSError:
    print('Failed creating direcotry %s' % path)

# Check if desired tool is installed
try:
  subprocess.run([args.tool, '--version'], capture_output=True)
except FileNotFoundError:
  print('%s not found nor installed' % args.tool)
  exit()

# Capture screen and compile video on KeyboardInterrupt
try:
  startCapture()
except KeyboardInterrupt:
  render2Video()
