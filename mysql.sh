dpkg -i mysql-apt-config_0.8.15-1_all.deb
service mysql start
mysql -u root << EOF
	ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'yourpassword';
	flush privileges;
	show databases;
	CREATE DATABASE IF NOT EXISTS twitter;
EOF

docker run -p 80:8000 -v /Users/rongfan/Projects/GitHub/my_twitter:/vagrant -it --name my_twitter_server my_twitter /bin/bash
docker exec -it my_twitter_server /bin/bash