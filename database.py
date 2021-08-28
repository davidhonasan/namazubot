import sqlite3

class Alarm:
  def __init__(self, alarm):
    self.id = alarm[0]
    self.alarm = alarm[1]
    self.notes = alarm[2]

class Database:
  def __init__(self):
    self.conn = sqlite3.connect('namazu.db')
    self.cursor = self.conn.cursor()
    self.create_tables()

  def __del__(self):
    self.conn.close()

  def create_tables(self):
    self.cursor.execute("""CREATE TABLE IF NOT EXISTS alarm_subscribers (
      id integer PRIMARY KEY,
      user_id text NOT NULL
      )""")
    self.cursor.execute("""CREATE TABLE IF NOT EXISTS alarms (
      id integer PRIMARY KEY,
      alarm integer NOT NULL,
      notes text NOT NULL
      )""")

  # Alarm Subscribers

  def get_alarm_subscribers(self):
    return self.cursor.execute('SELECT user_id FROM alarm_subscribers').fetchall()
  
  def check_alarm_subscriber(self, id):
    return self.cursor.execute('SELECT EXISTS( SELECT 1 FROM alarm_subscribers WHERE user_id = ?)', (id,)).fetchone()[0]

  def add_alarm_subscriber(self, user_id):
    self.cursor.execute('INSERT INTO alarm_subscribers VALUES (?,?)', (None,user_id))
    self.conn.commit()

  def remove_alarm_subscriber(self, id):
    self.cursor.execute('DELETE FROM alarm_subscribers WHERE user_id = ?', (id,))
    self.conn.commit()

  # Alarm
  def get_alarms(self):
    alarms = self.cursor.execute('SELECT * FROM alarms ORDER BY alarm ASC').fetchall()
    return list(map(Alarm, alarms))

  def get_alarm(self, id):
    alarm = self.cursor.execute('SELECT * FROM alarms WHERE id = ?', (id,)).fetchone()
    return Alarm(alarm)

  def get_earliest_alarm(self):
    alarm = self.cursor.execute('SELECT id, MIN(alarm), notes FROM alarms').fetchone()
    return Alarm(alarm)

  def check_alarm(self, id):
    return self.cursor.execute('SELECT EXISTS( SELECT 1 FROM alarms WHERE id = ?)', (id,)).fetchone()[0]

  def add_alarm(self, datetime, notes='Ship'):
    self.cursor.execute('INSERT INTO alarms VALUES (?,?,?)', (None, datetime, notes))
    self.conn.commit()

  def remove_alarm(self, id):
    self.cursor.execute('DELETE FROM alarms WHERE id = ?', (id,))
    self.conn.commit()

  