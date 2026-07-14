# Use PyMySQL (pure Python) as a drop-in replacement for mysqlclient so
# nobody needs system MySQL dev headers / a C compiler just to run this.
import pymysql

pymysql.install_as_MySQLdb()
