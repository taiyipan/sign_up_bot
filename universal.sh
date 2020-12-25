#!/usr/bin/env bash

# umbrella shell script that controls behaviors of universal.py execution

# hyperparams: weekly schedule (0: deactivated; 1: activated)
# Monday --> Thursday
monday=0
# Tuesday --> Friday
tuesday=0
# Wednesday --> Saturday
wednesday=0
# Thursday --> Monday
thursday=0
# Friday --> Tuesday
friday=0
# Saturday --> [None]
saturday=0
# Sunday --> Wednesday,Sunday
sunday=0

# determine whether to activate bots today (via short circuiting)
case $(date +%u) in
  1) [ $monday -eq 0 ] && exit 0;;
  2) [ $tuesday -eq 0 ] && exit 0;;
  3) [ $wednesday -eq 0 ] && exit 0;;
  4) [ $thursday -eq 0 ] && exit 0;;
  5) [ $friday -eq 0 ] && exit 0;;
  6) [ $saturday -eq 0 ] && exit 0;;
  7) [ $sunday -eq 0 ] && exit 0;;
  *) exit 1 # exit with error
esac

# check hostname, then set display_id, python_dir, bot_path, bot_count
if [ $(hostname) = "Galatea" ]; then
  display_id=:0.0
  python_dir=python3
  bot_path=/home/taiyi/sign_up_bot/universal.py
  bot_count=5
elif [ $(hostname) = "eternal" ]; then
  display_id=:1
  python_dir=python3
  bot_path=/home/taiyi/universal.py
  bot_count=4
elif [ $(hostname) = "sol.lan" ]; then
  display_id=:0
  python_dir=/usr/local/bin/python3
  bot_path=/Users/taiyipan/universal.py
  bot_count=2
elif [ $(hostname) = "raspberrypi" ]; then
  display_id=:0.0
  python_dir=python3
  bot_path=/home/taiyi/universal.py
  bot_count=1
else
  exit 1 # exit with error
fi

# export display_id value to shell
export DISPLAY=$display_id

# start multiple simultaneous instances of sign_up_bot program
for ((i = 0; i < $bot_count; i++))
do
  $python_dir $bot_path &
done

# exit shell script
exit 0
