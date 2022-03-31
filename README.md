# MYSQL初始化

```mysql
CREATE USER 'xhadmin'@'localhost' IDENTIFIED BY 'XianHang_123';

CREATE DATABASE naire;

GRANT ALL PRIVILEGES ON xhadmin.* TO 'naire'@'localhost';
FLUSH PRIVILEGES;
```
