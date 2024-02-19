/* (c) Grzegorz Blinowski 2000-2023 [TIN / PSI]
 * Andrii Gamalii 2023
 */

#include <arpa/inet.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include "protocol.h"

#define TRUE 1
#define BSIZE 1024
#define BUFBUFSIZE 65356

#define bailout(s) { perror(s); exit(1); }
#define notDone() TRUE

#define DEF_PORT 8888
#define DEF_ADDR "::1"

int moreWork(void) {
    return 1;
}

int main(int argc, char **argv) {
    int sock, msgsock, length, rval, ListenQueueSize = 5, read_bytes = 0;
    struct sockaddr_in6 server;
    char buf[BSIZE], bufbuf[65356];
    linked_list_t ll;

    sock = socket(AF_INET6, SOCK_STREAM, 0);
    if (sock<0)  bailout("opening stream socket");

/* dowiaz adres IPv6 do gniazda */
    server.sin6_family = AF_INET6;
//    inet_pton(AF_INET6, DEF_ADDR, &(server.sin6_addr));
    server.sin6_addr = in6addr_any;
    server.sin6_port = htons(DEF_PORT);
    if (bind(sock, (struct sockaddr *) &server, sizeof server) == -1)
    bailout("binding stream socket");

    /* wydrukuj na konsoli przydzielony port */
    length = sizeof(server);
    if (getsockname(sock,(struct sockaddr *) &server,&length) == -1)
    bailout("getting socket name");
    printf("Socket port #%d\n", ntohs(server.sin6_port));
    char str[INET6_ADDRSTRLEN];
    inet_ntop(server.sin6_family, &server.sin6_addr, str, INET6_ADDRSTRLEN);
    printf("Socket address: %s\n", str);
    /* zacznij przyjmować polaczenia... */
    listen(sock, ListenQueueSize);





//    /* initialize socket type, address and port */
//    memset(&hints, 0, sizeof(hints));
//    hints.ai_family = AF_INET6;
//    hints.ai_socktype = SOCK_STREAM;
//    hints.ai_flags = AI_PASSIVE;
//    if (getaddrinfo(0, DEF_PORT, &hints, &bindto_address) != 0) bailout("getting local address");
//
//    sock = socket(bindto_address->ai_family, bindto_address->ai_socktype, bindto_address->ai_protocol);
//    if (sock == -1) bailout("opening stream socket");
//
//    /* dowiaz adres do gniazda */
//    if (bind(sock, bindto_address->ai_addr, bindto_address->ai_addrlen)
//        == -1) bailout("binding stream socket");
//    freeaddrinfo(bindto_address);
//    printf("Socket port #%d\n", ntohs(server.sin6_port));
//    /* zacznij przyjmowa� polaczenia... */
//    listen(sock, ListenQueueSize);

    do {
        msgsock = accept(sock, (struct sockaddr *) 0, (socklen_t *) 0);
        if (msgsock == -1) {
            bailout("accept");
        } else
            do {
                memset(buf, 0, sizeof buf);
                if ((rval = read(msgsock, buf, BSIZE)) == -1) bailout("reading stream message");
                if (rval == 0){
                    printf("%s: Ending connection\n", argv[0]);
                }
                else {
                    if (read_bytes > BUFBUFSIZE){
                        bailout("Too many nodes in a list. I gotta head out...\n");
                    }
                    memcpy(bufbuf+read_bytes, buf, BSIZE);
                    if (rval == BSIZE){
                        read_bytes += rval;
                    } else {
                        deserialize_list(bufbuf, BUFBUFSIZE, &ll);
                        print_linked_list(&ll);
                        memset(bufbuf, 0, BUFBUFSIZE);
                        read_bytes = 0;
                    }
                }
            } while (rval != 0);
        close(msgsock);
        fflush(stdout);
    } while (moreWork());
    /*
     * gniazdo sock nie zostanie nigdy zamkniete jawnie,
     * jednak wszystkie deskryptory zostana zamkniete gdy proces
     * zostanie zakonczony (np w wyniku wystapienia sygnalu)
     */

    exit(0);
}
