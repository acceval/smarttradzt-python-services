How to operate on redis server:

1) open Terminal 1 - to start redis server
* Dont need to be in environment or main file folder
	- $ cd Documents/redis_try/	XX
	- $ source env/bin/activate	XX
	- $ redis-server		Yes

2) open Terminal 2 - start worker (open new terminal for multiple workers)
* Need to put to in main file folder because it will use the libraries
* Need to put in correct environment (env), else will get pickle error.
	- $ cd Documents/redis_try/LC	Yes
	- $ source env/bin/activate	Yes
	- $ rq worker			Yes

3) open Terminal 3 - start flask main file
	- $ cd Documents/redis_try/LC	Yes
	- $ source env/bin/activate	Yes
	- $ ./start-pyserver.sh		Yes

4) open Terminal 4 - start 'receive server' for background task
* Can put in another folder because different library
* Dont need to be in environment
	- $ cd Documents/redis_try/	Receive folder
	- $ source env/bin/activate	XX - go to environment with Flask
	- $ ./start-receive.sh		Yes
