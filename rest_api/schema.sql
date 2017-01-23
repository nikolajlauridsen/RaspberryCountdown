CREATE TABLE IF NOT EXISTS pomodoro (startTime INT, endTime INT, duration INT, cycles INT, task TEXT, FOREIGN KEY (task) REFERENCES tasks(name));
CREATE TABLE IF NOT EXISTS tasks (date INT, name TEXT);
CREATE TABLE IF NOT EXISTS activities (date INT, name TEXT);
CREATE TABLE IF NOT EXISTS timetrack (startTime INT, endTime INT, duration INT, activity TEXT, FOREIGN KEY (activity) REFERENCES activities(name));