/* (c) Grzegorz Blinowski 2000-2023 [TIN / PSI]
 * Andrii Gamalii 2023
 * */
#include <arpa/inet.h>
#include <err.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include "protocol.h"

#define DATA "Half a league, half a league . . ."
#define _USE_RESOLVER
#define USE_ARGS
#define DEFAULT_PORT 8888
#define DEFAULT_SRV_IP "127.0.0.1"

#define BSIZE 1024

#define bailout(s) { perror( s ); exit(1);  }
#define Usage() { errx( 0, "Usage: %s address-or-ip port number_of_nodes\n", argv[0]); }

int main(int argc, char *argv[])
{
    int sock = 0;
    struct sockaddr_in server;
    struct hostent *hp = NULL;
    char buf[BSIZE];
    int n_nodes = 0;

    printf("Starting...\n");

    /* Create socket. */
    sock = socket( AF_INET, SOCK_STREAM, 0 );
    if (sock == -1)
    bailout("opening stream socket");

    server.sin_family = AF_INET;

#ifdef USE_RESOLVER
    if (argc < 2) Usage();

    hp = gethostbyname2( argv[1], AF_INET );
    /* hostbyname() returns a struct with resolved host address  */
    if (hp == (struct hostent *) 0) {
        errx(2, "%s: unknown host\n", argv[1]);
    }

    memcpy( (char *) &server.sin_addr, (char *) hp->h_addr, hp->h_length);
    server.sin_port = htons(atoi(argv[2]));
#elif defined(USE_ARGS)
    if (argc < 4) Usage();
    inet_aton( argv[1], &server.sin_addr );
    server.sin_port = htons(atoi(argv[2]));
    n_nodes = atoi(argv[3]);
#else
    inet_aton( DEFAULT_SRV_IP, &server.sin_addr );
    server.sin_port = htons(DEFAULT_PORT);
#endif

    printf("Connecting...\n");
    if (connect(sock, (struct sockaddr *) &server, sizeof server) == -1)
    bailout("connecting stream socket");
    printf("Connected.\n");

    linked_list_t *ll = prepare_data(n_nodes);
    print_linked_list(ll);
    unsigned int buffer_len = 0;
    char *buffer_to_send = serialize_list(ll, &buffer_len);

    if (write( sock, buffer_to_send, buffer_len ) == -1)
    bailout("writing on stream socket");

    close(sock);
    exit(0);
}
