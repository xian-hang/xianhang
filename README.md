# MYSQL初始化

```mysql
CREATE USER 'xhadmin'@'localhost' IDENTIFIED BY 'XianHang_123';

CREATE DATABASE xhadmin;

GRANT ALL PRIVILEGES ON xhadmin.* TO 'xhadmin'@'localhost';
FLUSH PRIVILEGES;
```
