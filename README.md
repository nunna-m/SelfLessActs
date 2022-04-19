<h2>SelfLessActs: Photo Sharing Web Application</h2>  
<h4>Container Orchestrator service that can perform load balancing, auto-scaling and ensures fault tolerance. These functionalities have been implemented from scratch as a proof of concept.</h4>  
<br></br>  
<b>Assignment1</b>  
Used Amazon Web Services (AWS) to setup a Virtual Machine (VM), picked appropriate OS and installed web server on it. Created a mock webpage with HTML, CSS and JavaScript.  
<br></br>  

<b>Assignment2</b>  
Implement statelessness (server needn't keep track of any information). Every time an API call is made all information required is sent by the client. Cookies used to maintain state of user to showcase interaction of UI with the REST APIs. Used FLASK to serve REST API calls. MySQL to store databases. Python's Flask module used to interact with the database system. 
APIs include:  
1. getUserposts  
2. getUsers  
3. addUser  
4. removeUser  
5. checkPassword  
6. getCategory  
7. addCategory  
8. deleteCategory  
9. numPostsPerCategory  
10. getAllPosts  
11. upvotePost   
12. removePost  
13. uploadPost  
<br></br>  

<b>Assignment3</b>  
Setup and use docker containers, docker images. Two containers created to implement separate microservices for users and posts on the app. Old database split for each container eliminating the need for foreign key constraint.  
<br></br>  

<b>Assignment4</b>  
Separate instances created for users and posts.
Using Amazon's load balancer, created two target groups to perform path based routing to the two instances.  
<br></br>  

<b>Project</b>  
Built a container orchestrator that performs load balancing, auto-scaling and ensures fault tolerance from scratch.The load balancer used Round-robin policy. Fault tolerance is ensured using heartbeat mechanism that polls each container at a fixed frequency, and if container fails to respond the orchestrator initiates a replacement of that container with a healthy new container. Finally, the auto-scaler dynamically scales the number of containers up or down based on number of incoming requests. Number of containers running at given point in time = (K/20)+1 where K is the number of requests received in the last 2 minutes. Thus, scaling happens every 2 minutes.
All these specifics can be set to required number using JSON file:  
number of containers  
starting port number  
heartbeat frequency  
threshold number of requests after which scaling occurs  


<br></br>  
<br></br>  
