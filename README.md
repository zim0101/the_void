        ████████╗██╗░░██╗███████╗ ██╗░░░██╗░█████╗░██╗██████╗░
        ╚══██╔══╝██║░░██║██╔════╝ ██║░░░██║██╔══██╗██║██╔══██╗
        ░░░██║░░░███████║█████╗░░ ╚██╗░██╔╝██║░░██║██║██║░░██║
        ░░░██║░░░██╔══██║██╔══╝░░ ░╚████╔╝░██║░░██║██║██║░░██║
        ░░░██║░░░██║░░██║███████╗ ░░╚██╔╝░░╚█████╔╝██║██████╔╝
        ░░░╚═╝░░░╚═╝░░╚═╝╚══════╝ ░░░╚═╝░░░░╚════╝░╚═╝╚═════╝░

# [ The Void ] - Where Everyone is Anonymous

### How to run the client application
1. Clone the git repository and get into the repository:
   ``git clone https://github.com/zim0101/the_void.git``
2. Build the client application:
   ``docker build -t chat-client -f Dockerfile.client .``
3. Run the client application:
   ``docker run -it --rm --name chat-client chat-client``
4. After running the client application, it will ask for your anonymous name. 
5. Then the tcp url and a secret key which you will obtain from the person who hosted the server.
