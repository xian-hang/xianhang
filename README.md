# MYSQL初始化

```mysql
CREATE USER 'xhadmin'@'localhost' IDENTIFIED BY 'XianHang_123';

CREATE DATABASE xianhang;

GRANT ALL PRIVILEGES ON xianhang.* TO 'xhadmin'@'localhost';
FLUSH PRIVILEGES;
```
