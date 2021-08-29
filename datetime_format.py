import datetime
import math

def styled_datetime(datetime):
  return datetime.strftime('%a %d/%m/%Y %H:%M:%S %Z')

def styled_timedelta(timedelta):
  formatted_string = ''
  days = timedelta.days
  hours = math.floor(timedelta.seconds / 3600)
  minutes = math.floor((timedelta.seconds % 3600) / 60)
  seconds = timedelta.seconds % 60
  if days > 0:
    formatted_string += '{} day{} '.format(days, 's' if days > 1 else '') 
  if hours > 0:
    formatted_string += '{} hour{} '.format(hours, 's' if hours > 1 else '') 
  if minutes > 0:
    formatted_string += '{} minute{} '.format(minutes, 's' if minutes > 1 else '') 
  if seconds > 0:
    formatted_string += '{} second{}'.format(seconds, 's' if seconds > 1 else '')
  return formatted_string