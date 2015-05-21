```sh
$PORT=6379
# Download
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
pushd redis-stable

# Fix dependencies, if necessary
pushd deps
make hiredis jemalloc linenoise lua
popd

make

# if test
    yum install -y tcl
    make test
# fi

sudo make install

# Proper install
sudo mkdir /etc/redis
sudo mkdir /var/redis

sudo cp redis.conf /etc/redis/$PORT.conf
sudo cp utils/redis_init_script /etc/init.d/redis_$PORT

sed -i "s,REDISPORT=6379,REDISPORT=$PORT," /etc/init.d/redis_$PORT

sudo sed -i 's/daemonize no/daemonize yes/' /etc/redis/$PORT.conf
sudo sed -i "s,port 6379,port $PORT," /etc/redis/$PORT.conf
sudo sed -i "s,logfile \"\",logfile \"/var/log/redis_$PORT.log\"," /etc/redis/$PORT.conf
sudo sed -i "s,dir ./,dir /var/redis/$PORT," /etc/redis/$PORT.conf

popd

sudo service redis_6379 start
```
