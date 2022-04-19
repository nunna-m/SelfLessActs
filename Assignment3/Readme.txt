sudo docker create network mynet

docker run -it --net mynet -p 8000:3000 -p 3036:3036 -p 80:80 -e TEAM_ID="CC_187_221_242" -name=acts abhisai21/acts_gun sh

docker run -it --net mynet -p 8080:3000 -p 3037:3036 -e TEAM_ID="CC_187_221_242" -name=users abhisai21/users_gun sh

/usr/bin/mysqld --user=root &

nginx -g 'daemon on;'

gunicorn act.py:app --daemon