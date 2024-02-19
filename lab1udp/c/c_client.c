/* (c) Grzegorz Blinowski 2000-2023 [TIN / PSI]
 * Kod rozwinięty przez: Igor Matynia oraz Bartłomiej Pełka
 * */
#include <arpa/inet.h>
#include <err.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/poll.h>
#include "protocol.h"

#define bailout(s) {perror(s); exit(1); }
#define Usage() { errx( 0, "Usage: %s <host> <port> <count> <delay-in-ms>\n", argv[0]); }
#define timeinms(tv) ( (tv.tv_sec) * 1000.0 + (tv.tv_usec) / 1000.0 )
#define BUFSIZE 1024
#define TIMEOUT_SEC 1

void print_address(const char *s, struct sockaddr *address, socklen_t addrlen) {
    char addrbuffer[NI_MAXHOST];

    getnameinfo(address, addrlen, addrbuffer, NI_MAXHOST, 0, 0, NI_NUMERICHOST);
    printf("%s %s\n", s, addrbuffer);
}


int main(int argc, char *argv[]) {
    int sock;
    struct sockaddr_in server;
    struct hostent *hp;
    char databuf[BUFSIZE], serverdata[BUFSIZE];
    long int packet_num = 0, udelay;

    ssize_t nread;
    struct sockaddr_storage server_addr;
    socklen_t server_addrlen;
    int dataLen = 50;

    if (argc != 5) {
        Usage();
    }

    udelay = atol(argv[4]) * 1000;

    /* Create socket. */
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock == -1) bailout("opening stream socket");

    /* uzyskajmy adres IP z nazwy . */
    server.sin_family = AF_INET;
    hp = gethostbyname2(argv[1], AF_INET);

    /* hostbyname zwraca strukture zawierajaca adres danego hosta */
    if (hp == (struct hostent *) 0) {
        errx(2, "%s: unknown host\n", argv[1]);
    }
    printf("address resolved...\n");

    memcpy((char *) &server.sin_addr, (char *) hp->h_addr, hp->h_length);
    server.sin_port = htons(atoi(argv[2]));

    connect(sock, (struct sockaddr *) &server, sizeof(server));
    print_address("sending packets to: ", (struct sockaddr *) &server, sizeof(server));
    while (packet_num < atol(argv[3])) {
        memset(databuf, '\0', BUFSIZE);
        memset(serverdata, '\0', BUFSIZE);

        protocol_header_t header = {
                .content_length = dataLen,
                .sequence_number = packet_num,
        };
        long packetSize = generate_data_packet(databuf, &header);

        struct pollfd fds[1];
        fds[0].fd = sock;
        fds[0].events = POLLIN;

        int resend = 1;
        while(resend)
        {
            if (send(sock, databuf, packetSize, 0) < 0)
                perror("Error sending packet");

            int ready = poll(fds, 1, TIMEOUT_SEC * 1000);

            if (ready == 0) {
                printf("Timeout occurred. Resending message...\n");
            } else if (ready < 0) {
                perror("Error in poll");
            } else {
                resend = 0;
            }
        }

        server_addrlen = sizeof(server_addr);
        nread = recvfrom(sock, serverdata, BUFSIZE, 0,
                         (struct sockaddr *) &server, &server_addrlen);
        if (nread <0 ) {
            fprintf(stderr, "failed recvfrom\n");
            usleep(TIMEOUT_SEC * 1000000);
        } else {
            protocol_header_t* packet_header = (protocol_header_t*)serverdata;
            printf("Received from server: [len:%d, seq:%d] %s\n", packet_header->content_length, packet_header->sequence_number, serverdata+HEADER_SIZE);
            packet_num++; // zwiększenie bo dostaliśmy potwierdzenie że pakiet przyszedł
            usleep(udelay);
        }
    }

    close(sock);
    exit(0);
}
