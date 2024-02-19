/* (c) Grzegorz Blinowski 2000-2023 [TIN / PSI]
 * Kod rozwinięty przez: Igor Matynia oraz Bartłomiej Pełka
 * */
#include <err.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>
#include "protocol.h"

#define BUF_SIZE 500

#define bailout(s) { perror( s ); exit(1);  }
#define Usage() { errx( 0, "Usage: %s address-or-ip [port]\n", argv[0]); }
#define timeinms(tv) ( (tv.tv_sec) * 1000.0 + (tv.tv_usec) / 1000.0 )

int working = 1;

int doWork() {
    return working;
}

void server(in_port_t port) {
    int sfd, s;
    char buf[BUF_SIZE];
    ssize_t nread;
    socklen_t peer_addrlen;
    struct sockaddr_in server;
    struct sockaddr_storage peer_addr;

    if ((sfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) bailout("socker() ");

    server.sin_family = AF_INET;  /* Server is in Internet Domain */
    server.sin_port = port;         /* Use any available port      */
    server.sin_addr.s_addr = INADDR_ANY; /* Server's Internet Address   */

    if ((s = bind(sfd, (struct sockaddr *) &server, sizeof(server))) < 0) bailout("bind() ");
    printf("bind() successful\n");

    /* Read datagrams and echo them back to sender. */
    printf("waiting for packets...\n");

//    int i = 0;
    while (doWork()) {
//        i++;
        char host[NI_MAXHOST], service[NI_MAXSERV];

        peer_addrlen = sizeof(peer_addr);
        nread = recvfrom(sfd, buf, BUF_SIZE, 0,
                         (struct sockaddr *) &peer_addr, &peer_addrlen);
        printf("recvfrom ok\n");
        if (nread < 0) {
            fprintf(stderr, "failed recvfrom\n");
            continue;               /* Ignore failed request */
        }

        s = getnameinfo((struct sockaddr *) &peer_addr, peer_addrlen, host, NI_MAXHOST,
                        service, NI_MAXSERV, NI_NUMERICSERV);
        if (s == 0) {
            printf("Received %zd bytes from %s:%s\n", nread, host, service);

            int data_check = check_packet(buf);
            printf("Packet check: %d\n", data_check);

            protocol_header_t* header = (protocol_header_t*)buf;
            size_t new_length = generate_response_packet(buf, header, data_check);
//            if(i%10==0)
                sendto(sfd, buf, new_length, 0, (struct sockaddr *) &peer_addr, peer_addrlen);
        } else {
            fprintf(stderr, "getnameinfo() error: %s\n", gai_strerror(s));
            continue;
        }
    }
}

int main(int argc, char *argv[]) {

    if (argc != 2) Usage();
    in_port_t port = htons(atoi(argv[1]));
    server(port);
}